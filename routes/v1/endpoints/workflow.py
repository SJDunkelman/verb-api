from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from api.dependencies import get_db
from api.utils.security import get_current_user
from api.models.workflow import WorkflowInDB
from api.models.workflow_template import WorkflowTemplateInDB
from api import schemas
from uuid import UUID
from postgrest.exceptions import APIError

router = APIRouter()


@router.get("/", response_model=list[WorkflowInDB])
async def get_all_workflows(db=Depends(get_db), user=Depends(get_current_user)):
    user_workflow_results = db.rpc("get_accessible_workflows", params={"user_id": user.id}).execute()
    workflows = [WorkflowInDB(**{
        "id": workflow["w_id"],
        "name": workflow["w_name"],
        "created_at": workflow["w_created_at"],
    }) for workflow in user_workflow_results.data]
    return workflows


# TODO: Re-add user=Depends(get_current_user)
@router.get("/templates", response_model=list[WorkflowTemplateInDB])
async def get_all_workflow_templates(db=Depends(get_db)):
    workflow_template_results = db.table('workflow_template').select('*').execute()
    if not workflow_template_results.data:
        raise HTTPException(status_code=404, detail="No workflow templates found")
    workflow_templates = [WorkflowTemplateInDB(**{
        "id": workflow_template["id"],
        "name": workflow_template["name"],
        "description": workflow_template["description"]
    }) for workflow_template in workflow_template_results.data]
    return workflow_templates


@router.get("/{workflow_id}", response_model=WorkflowInDB)
async def get_workflow(workflow_id: UUID, db=Depends(get_db), user=Depends(get_current_user)):
    workflow = db.table('workflow').select('*').eq('id', workflow_id).execute()
    if not workflow.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow['created_by_user_id'] != user.id:
        raise HTTPException(status_code=403, detail="User does not have access to this workflow")
    return workflow


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.WorkflowResponse)
async def create_workflow(new_workflow: schemas.WorkflowCreate,
                          db=Depends(get_db),
                          user=Depends(get_current_user)
                          ) -> schemas.WorkflowResponse:
    # Check template exists
    try:
        workflow_template_result = db.table('workflow_template').select('id').eq('id',
                                                                                 new_workflow.template_id).single().execute()
    except APIError:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    # Create new workflow instance
    try:
        workflow_result = db.table('workflow').insert({
            'name': new_workflow.name,
            'created_by_user_id': str(user.id),
            'template_id': str(new_workflow.template_id)
        }).execute()
        new_workflow_id = workflow_result.data[0]['id']
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't create workflow")

    # Get nodes and edges from template and add under workflow
    template_node_results = db.rpc("get_workflow_template_nodes", params={
        "workflow_template_id": str(new_workflow.template_id)
    }).execute()

    nodes_to_insert = [
        {
            "workflow_id": new_workflow_id,
            "name": node['workflow_template_node_name'],
            "description": node['workflow_template_node_description'],
            "node_id": node['node_id'],
            "base_type": node['node_base_type'],
            "class_name": node['node_class_name'],
        } for node in template_node_results.data
    ]
    try:
        # Don't include the base_type and class_name in insert as those are in the node table not workflow_node
        db.table('workflow_node').insert([
            {
                "workflow_id": new_workflow_id,
                "name": node['name'],
                "description": node['description'],
                "node_id": node['node_id'],
            } for node in nodes_to_insert
        ]).execute()
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't create workflow nodes")

    # Fetch the newly created workflow nodes to get their UUIDs
    new_nodes = db.table('workflow_node').select('id, node_id').eq('workflow_id', new_workflow_id).execute()

    # Create a mapping from node_id (shared by template and workflow) to new workflow node UUID
    node_id_to_workflow_node_id = {node['node_id']: node['id'] for node in new_nodes.data}
    template_node_id_to_workflow_node_id = {node['id']: node_id_to_workflow_node_id[node['node_id']] for node in
                                            template_node_results.data}

    # Get edges and rules from template and add to new workflow
    workflow_template_edges_and_rules = db.rpc("get_workflow_template_edges_and_rules", params={
        "workflow_template_id": str(new_workflow.template_id)
    }).execute()

    # Prepare the edges to be inserted into workflow_node_edge, updating node IDs
    edges_to_insert = []
    for edge in workflow_template_edges_and_rules.data:
        from_node_uuid = template_node_id_to_workflow_node_id.get(edge['from_node_id'])
        to_node_uuid = template_node_id_to_workflow_node_id.get(edge['to_node_id'])
        if from_node_uuid and to_node_uuid:
            edges_to_insert.append({
                'workflow_id': new_workflow_id,
                'from_node_id': from_node_uuid,
                'to_node_id': to_node_uuid
            })

    try:
        db.table('workflow_node_edge').insert(edges_to_insert).execute()
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't create workflow edges")

    # Fetch the newly created workflow edges to get their UUIDs
    new_edges = db.table('workflow_node_edge').select('id, from_node_id, to_node_id').eq('workflow_id',
                                                                                         new_workflow_id).execute()

    # Create a mapping from template edge_id to new workflow edge UUID
    edge_id_map = {}
    for edge in new_edges.data:
        for template_edge in workflow_template_edges_and_rules.data:
            # Translate template node IDs (bigint) to workflow node UUIDs
            from_node_uuid = template_node_id_to_workflow_node_id.get(template_edge['from_node_id'])
            to_node_uuid = template_node_id_to_workflow_node_id.get(template_edge['to_node_id'])

            # Check against the translated UUIDs
            if from_node_uuid == edge['from_node_id'] and to_node_uuid == edge['to_node_id']:
                edge_id_map[template_edge['edge_id']] = edge['id']

    # Prepare the edge rules to be inserted into workflow_edge_rule
    rules_to_insert = []
    for edge_rule in workflow_template_edges_and_rules.data:
        template_edge_id = edge_rule['edge_id']
        new_edge_id = edge_id_map.get(template_edge_id)

        # Check if the edge has an associated rule_id and the new edge ID is found
        if new_edge_id and edge_rule.get('rule_id'):
            rules_to_insert.append({
                'edge_id': new_edge_id,
                'rule_id': edge_rule['rule_id'],
                'rule_order': edge_rule['rule_order']
            })

    try:
        db.table('workflow_edge_rule').insert(rules_to_insert).execute()
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't create workflow edge rules")

    # Add the predefined pathways from the template to the workflow
    try:
        template_pathway_results = db.rpc('get_workflow_pathways_from_template', params={
            "template_workflow_id": str(new_workflow.template_id),
            "new_workflow_id": new_workflow_id
        }).execute()
        workflow_pathway = db.table('workflow_pathway_sequence').insert([
            {
                'pathway_id': step['pathway_id'],
                'node_id': step['workflow_node_id'],
                'sequence_order': step['sequence_order']
            }
            for step in template_pathway_results.data]).execute()
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't create new workflow pathways")

    nodes = [
        schemas.WorkflowNode(id=node_id_to_workflow_node_id[node['node_id']],
                             node_id=node['node_id'],
                             name=node['name'],
                             description=node['description'],
                             base_type=node['base_type'],
                             class_name=node['class_name'],
                             context_items={})
        for node in nodes_to_insert
    ]

    edges_dict = {edge['id']: schemas.Edge(id=edge['id'],
                                           from_node_id=edge['from_node_id'],
                                           to_node_id=edge['to_node_id'])
                  for edge in new_edges.data}

    for edge_rule in workflow_template_edges_and_rules.data:
        if 'rule_id' in edge_rule and edge_rule['rule_id']:
            # Retrieve the new edge ID from the edge_id_map
            new_edge_id = edge_id_map.get(edge_rule['edge_id'])

            # Check if this new edge ID exists in edges_dict and add the rule
            if new_edge_id and new_edge_id in edges_dict:
                edge_rule_obj = schemas.EdgeRule(id=edge_rule['rule_id'],
                                                 class_name=edge_rule['rule_class_name'],
                                                 description=edge_rule['rule_description'],
                                                 rule_order=edge_rule['rule_order'])
                edges_dict[new_edge_id].rules.append(edge_rule_obj)

    edges = list(edges_dict.values())

    # Update user last viewed workflow
    db.table('user').update({'last_viewed_workflow_id': new_workflow_id}).eq('id', user.id).execute()

    return schemas.WorkflowResponse(**{
        "id": new_workflow_id,
        "name": new_workflow.name,
        "created_at": workflow_result.data[0]['created_at'],
        "is_private": new_workflow.is_private,
        "stage": workflow_result.data[0]['stage'],
        "nodes": nodes,
        "edges": edges
    })


# @router.put("/{workflow_id}", response_model=WorkflowInDB)
# async def update_workflow(workflow_id: str, workflow_data: WorkflowCreate, db=Depends(get_db),
#                           user=Depends(get_current_user)):
#     # Update an existing workflow_graph
#
#     if not updated_workflow:
#         raise HTTPException(status_code=404, detail="Workflow not found")
#
#     updated_workflow = db.table('workflow_graph').update(workflow_data.dict()).eq('id', workflow_id).returning('*').execute()
#
#     if workflow['created_by_user_id'] != user.id:
#         raise HTTPException(status_code=403, detail="User does not have access to this workflow_graph")
#     return updated_workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    workflow = db.table('workflow').select('created_by_user_id').eq('id', workflow_id).execute()
    if workflow['created_by_user_id'] != user.id:
        raise HTTPException(status_code=403, detail="User does not have access to this workflow_graph")
    deleted = db.table('workflow').delete().eq('id', workflow_id).execute()
    if not deleted.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"detail": "Workflow deleted successfully"}


@router.get("/{workflow_id}/diagram")
async def get_workflow_state(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    # Get workflow nodes
    # Return data based on node type, name and node ID
    pass


@router.get("/{workflow_id}/stage")
async def get_workflow_stage(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    stage_response = db.table('workflow').select('stage').eq('id', workflow_id).execute()
    if not stage_response.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"stage": stage_response['stage']}


@router.post("/{workflow_id}/simulate")
async def simulate_workflow(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    # Logic to start a simulation for a specific workflow_graph
    # This might involve setting a flag in the database or triggering a simulation process
    # Placeholder for simulation logic
    return {"message": "Simulation started for workflow_graph {}".format(workflow_id)}


# POST /workflow_graph/{workflow_id}/activate
@router.post("/{workflow_id}/activate")
async def activate_workflow(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    # Logic to activate a specific workflow_graph
    # This might involve updating a field in the database
    # Placeholder for activation logic

    # Check that the workflow isn't already live
    # Check that workflow has been successfully QA'd
    return {"message": "Workflow {} activated".format(workflow_id)}

# # POST /workflow_graph/{workflow_id}/deactivate
# @router.post("/{workflow_id}/deactivate")
# async def deactivate_workflow(workflow_id: str, db=Depends(get_db), user=Depends(get_current_user)):
#     # Logic to deactivate a specific workflow_graph
#     # This might involve updating a field in the database
#     # Placeholder for deactivation logic
#     return {"message": "Workflow {} deactivated".format(workflow_id)}


# Feedback and Interaction during Simulation:

# # POST /workflow_graph/{workflow_id}/feedback
# @router.post("/{workflow_id}/feedback")
# async def submit_workflow_feedback(workflow_id: str, feedback: str, db=Depends(get_db),
#                                    user=Depends(get_current_user)):
#     # Logic to handle feedback submission during a workflow_graph simulation
#     # This might involve storing the feedback in the database
#     # Placeholder for feedback submission logic
#     return {"message": "Feedback received for workflow_graph {}".format(workflow_id)}
