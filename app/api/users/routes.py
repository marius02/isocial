from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_users import models, exceptions
from fastapi_users.manager import BaseUserManager

from app.api.users.schemas import AuthPassChange, Auth, Question

from app.db.db_config import User
from app.api.users.services import get_user_manager, current_active_user


router = APIRouter(prefix="/auth", tags=["Authentication and authorization"])


@router.post('/changepassword/')
async def password_change(pass_change: AuthPassChange, user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):

    auth = Auth(username=pass_change.email, password=pass_change.password)

    valid_user = await user_manager.authenticate(auth)

    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current Password is not correct")
    try:
        await user_manager.reset_password_user(valid_user, pass_change.new_password)
        return {"message": f"Password updated successfully "}
    except exceptions.InvalidPasswordException as e:
        print("error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "PASSWORD_REQUREMENT_NOT_MET",
                "reason": "Password should be minimum 5 and maximum 16 characters \n Should contain atleast 1 digit \n Should contain atleast 1 alphabet \n Should contain atleast 1 special character"
                }
        )




@router.get("/email-verification")
async def email_verificatrion(token, user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):
    try:
        result = await user_manager.verify(token=token)
    
        if result.is_verified:
            return {
                "detail": {
                    "code": "USER_VERIFIED",
                    "reason": user.email
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={ 
                    "code": "REGISTER_USER_EXPIRED",
                    "reason" : "Activation email is expired, please re request activation link"
                }
            )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={ 
                    "code": "REGISTER_USER_ACTIVATED",
                    "reason" : "You has been already verified"
                }
            )

@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router.get("/account/questions", response_model=list[Question])
async def get_questions(user: User = Depends(current_active_user)):
    questions = [
        {
            "question_id": "94620adf-514d-4c7b-b461-65bae72d3fce",
            "text": "Summarize the video comments"
        },
        {
            "question_id": "cb8c96b4-fa60-4cb1-995d-2d72fd6a1a55",
            "text": "Excluding negative comments, itemize a list of constructive feedback"
        },
        {
            "question_id": "419796c2-3504-42b4-82e8-dbfd1c91d8c5",
            "text": "How did the users find the video useful?"
        }
    ]

    return questions
