from schemas.workflow_diagram import WorkflowDiagram, Node, NodeData, Edge


def find_starting_node(edge_data, node_data):
    dependent_nodes = {edge['to_node_id'] for edge in edge_data}
    for node in node_data:
        if node['node_id'] not in dependent_nodes:
            return node
    return None  # Handle the case where no starting node is found


def build_dependency_tree(nodes, edges):
    # Convert the list of nodes to a dictionary for easy lookup
    nodes_dict = {node['workflow_node_id']: node for node in nodes}

    # Create a dictionary to keep track of incoming edges to each node
    incoming_edges = {node['workflow_node_id']: 0 for node in nodes}
    for edge in edges:
        to_node = edge['to_node_id']
        if to_node in incoming_edges:  # ensuring the node exists in the nodes list
            incoming_edges[to_node] += 1
    # Start with nodes that have no incoming edges
    roots = [node_id for node_id, count in incoming_edges.items() if count == 0]

    # Function to find dependent nodes
    def find_dependents(current_level):
        next_level = []
        for node_id in current_level:
            for edge in edges:
                if edge['from_node_id'] == node_id:
                    to_node = edge['to_node_id']
                    incoming_edges[to_node] -= 1
                    if incoming_edges[to_node] == 0:
                        next_level.append(to_node)
        return next_level

    # Build the tree
    tree = []
    while roots:
        tree.append(roots)
        roots = find_dependents(roots)

    # Convert node IDs to node information
    tree_with_node_info = [[nodes_dict[node_id] for node_id in level if node_id in nodes_dict] for level in tree]

    return tree_with_node_info


def create_edges(edge_data: list[dict]):
    edges = []
    for idx, edge in enumerate(edge_data):
        edges.append(Edge(
            id=f"e{idx + 1}-{idx + 2}",
            source=edge['from_node_id'],
            target=edge['to_node_id'],
            animated=True
        ))
    return edges


def transform_node(node_data: dict, index_within_level: int, level: int):
    # Map base_type to the corresponding node type for frontend component
    type_map = {
        'INPUT': 'inputNode',
        'PROCESS': 'processNode',
        'OUTPUT': 'outputNode'
    }
    x_position = 300 * index_within_level
    y_position = 120 * level
    return Node(
        id=node_data['workflow_node_id'],
        position={'x': x_position, 'y': y_position},
        data=NodeData(label=node_data['name'], description=node_data['description']),
        type=type_map.get(node_data['base_type'], 'defaultType')  # defaultType is a fallback
    )


def create_workflow_diagram(workflow_node_data: list[dict], workflow_edge_data: list[dict]):
    # First, build the dependency tree
    dependency_tree = build_dependency_tree(workflow_node_data, workflow_edge_data)

    # Transform nodes with positioning based on their level and index within the level
    nodes = []
    for level, level_nodes in enumerate(dependency_tree):
        for index, node_data in enumerate(level_nodes):
            transformed_node = transform_node(node_data=node_data,
                                              level=level,
                                              index_within_level=index)
            nodes.append(transformed_node)

    edges = create_edges(workflow_edge_data)
    return WorkflowDiagram(nodes=nodes, edges=edges)


if __name__ == "__main__":
    edge_results_data = [{'id': '02489d28-6340-4f96-9c1f-f3e91b195ac8', 'workflow_id': '2d82e45b-099b-4dac-b325-9cb313aaf1d0', 'from_node_id': 'c99468c5-2804-4b1c-8a37-f34f67a30435', 'to_node_id': 'f51b4779-0fe3-4b5d-9ffd-022c36899afe'}, {'id': 'b8ffae84-d0f6-47ab-bae2-623259041ef5', 'workflow_id': '2d82e45b-099b-4dac-b325-9cb313aaf1d0', 'from_node_id': 'c99468c5-2804-4b1c-8a37-f34f67a30435', 'to_node_id': '37e3a4ff-c0ad-402e-a363-7b5ccbc7b6cc'}, {'id': '839e5008-e514-4e12-bbc8-6e926b725b82', 'workflow_id': '2d82e45b-099b-4dac-b325-9cb313aaf1d0', 'from_node_id': '37e3a4ff-c0ad-402e-a363-7b5ccbc7b6cc', 'to_node_id': 'f51b4779-0fe3-4b5d-9ffd-022c36899afe'}, {'id': '7d67c53d-f5fd-4a39-b664-8dca692e4123', 'workflow_id': '2d82e45b-099b-4dac-b325-9cb313aaf1d0', 'from_node_id': '65d20d39-64ef-465b-b4d5-0af42b5928f0', 'to_node_id': 'c99468c5-2804-4b1c-8a37-f34f67a30435'}]
    node_results_data = [{'workflow_node_id': '65d20d39-64ef-465b-b4d5-0af42b5928f0', 'class_name': 'InAppMessageNode', 'base_type': 'INPUT', 'node_id': '9bc7ba9c-2073-4362-b823-376633a2cd75', 'name': 'Comet App Chat', 'description': 'Send messages on the comet app to the workflow'}, {'workflow_node_id': 'c99468c5-2804-4b1c-8a37-f34f67a30435', 'class_name': 'GenerateLeadListLinkedInNode', 'base_type': 'PROCESS', 'node_id': 'bd83956a-5ba1-46ba-81ae-e65d9c1ed009', 'name': 'Generate lead list from LinkedIn', 'description': 'Use LinkedIn Sales Navigator to find people that match your target customer'}, {'workflow_node_id': 'f51b4779-0fe3-4b5d-9ffd-022c36899afe', 'class_name': 'EnrichedLeadListExcelNode', 'base_type': 'OUTPUT', 'node_id': '8d5ee564-6601-417a-873b-4156602b5eb3', 'name': 'Lead list Excel files', 'description': 'Download the lead list from LinkedIn that contains the profiles as well as verified email addresses.'}, {'workflow_node_id': '37e3a4ff-c0ad-402e-a363-7b5ccbc7b6cc', 'class_name': 'EnrichLinkedInLeadListNode', 'base_type': 'PROCESS', 'node_id': '1ea00ca2-899a-409d-975e-00dbb6ebaffc', 'name': 'Enrich LinkedIn Leads', 'description': 'Get profile information and verified email addresses from the LinkedIn Lead search results'}]
    workflow_diagram = create_workflow_diagram(node_results_data, edge_results_data)
