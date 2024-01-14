from fastapi import APIRouter, Depends
from api.dependencies import get_db
from api.utils.security import get_current_user

router = APIRouter()


@router.post("/onboarded", status_code=201, response_model=bool)
async def update_user_onboarding(user=Depends(get_current_user), db=Depends(get_db)):
    db.table('user').update({'onboarded': True}).eq('id', user.id).execute()
    return True


@router.get("/profile", status_code=200)
async def get_user_profile(user=Depends(get_current_user), db=Depends(get_db)):
    pass
