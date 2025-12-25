from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.serializers import UserResponse
from app.services.auth.register_service import UserService
from app.validations.register_validation import UserRegistrationRequest

router = APIRouter(prefix="/auth", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        user_data: UserRegistrationRequest,
        db: AsyncSession = Depends(get_db),
):
    user = await UserService.create_user(db, user_data)
    return user
