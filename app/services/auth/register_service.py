from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash

from app.database.redis_client import cache
from app.models.profile import Profile
from app.models.user import User
from app.serializers import UserResponse
from app.validations.register_validation import UserRegistrationRequest


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        return check_password_hash(hashed_password, password)

    # ---------- queries ----------

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # ---------- create ----------

    @staticmethod
    async def create_user(
            db: AsyncSession,
            user_data: UserRegistrationRequest,
    ) -> UserResponse:
        try:
            if await UserService.get_user_by_email(db, str(user_data.email)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            user = User(
                email=str(user_data.email),
                password=UserService.hash_password(user_data.password),
                is_active=True,
            )
            db.add(user)
            await db.flush()

            db_profile = Profile(
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            db.add(db_profile)

            await db.commit()
            await db.refresh(user, attribute_names=["profile"])

            user_response = UserResponse.model_validate(user)
            await cache.setex(
                900,
                user_response.model_dump_json(),
                "user",
                str(user_response.id),
            )

            return user_response

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error",
            )

        except HTTPException:
            await db.rollback()
            raise

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating user",
            )
