from fastapi import APIRouter, HTTPException, Depends, Response
from gotrue.errors import AuthApiError
from postgrest.exceptions import APIError
from dependencies import get_db
from schemas.auth import UserLogin, UserLoginResponse
from models.workflow import WorkflowInDB


router = APIRouter()


@router.post("/login", status_code=200, response_model=UserLoginResponse)
async def login(response: Response, user: UserLogin, db=Depends(get_db)):
    try:
        auth_response = db.auth.sign_in_with_password({'email': user.email, 'password': user.password})
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=e.message)

    access_token = auth_response.session.access_token
    user_id = auth_response.user.id
    # Set the access token in an HTTP-only cookie
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='Lax')

    user_result = db.table('user').select('id', 'first_name', 'onboarded', 'last_viewed_workflow_id').eq('id',
                                                                                                         user_id).single().execute()
    try:
        user_workflow_results = db.rpc("get_accessible_workflows", params={"user_id": user_id}).execute()
    except APIError:
        raise HTTPException(status_code=400, detail="Couldn't fetch user workflows")
    user_workflows = [WorkflowInDB(**{
        "id": workflow["w_id"],
        "name": workflow["w_name"],
        "created_at": workflow["w_created_at"],
        "is_private": workflow["w_is_private"],
        "stage": workflow["w_stage"],
    }) for workflow in user_workflow_results.data]
    user_workflows.sort(key=lambda x: x.created_at, reverse=True)  # Most recent first

    return UserLoginResponse(
        access_token=access_token,
        user_id=user_id,
        first_name=user_result.data["first_name"],
        onboarded=user_result.data["onboarded"],
        last_viewed_workflow_id=user_result.data["last_viewed_workflow_id"],
        workflows=user_workflows
    )


@router.post("/logout", status_code=200)
async def logout(db=Depends(get_db)):
    db.auth.sign_out()
    return {"status": "ok"}


# @router.post("/test", status_code=200)
# async def test(user=Depends(get_current_user)):
#     return user


@router.post("/test", status_code=200)
async def test(db=Depends(get_db)):
    res = db.table('user').select('*').execute()
    return res.data