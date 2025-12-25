from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash

from app.database.redis_client import redis_client
from app.models.profile import Profile
from app.models.user import User
from app.validations.register_validation import UserRegistrationRequest


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return check_password_hash(hashed_password, password)

    # ---------- queries ----------

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # ---------- create ----------

    @staticmethod
    async def create_user(
            db: AsyncSession,
            user_data: UserRegistrationRequest,
    ) -> User:
        try:
            if await UserService.get_user_by_email(db, str(user_data.email)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            if await UserService.get_user_by_username(db, user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

            db_user = User(
                email=str(user_data.email),
                username=user_data.username,
                hashed_password=UserService.hash_password(user_data.password),
                is_active=True,
                is_verified=False,
            )
            db.add(db_user)
            await db.flush()

            db_profile = Profile(
                user_id=db_user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
            )
            db.add(db_profile)

            await db.commit()
            await db.refresh(db_user, attribute_names=["profile"])

            # Redis MUST be async
            await redis_client.setex(
                f"user:{db_user.id}",
                3600,
                db_user.email,
            )

            return db_user

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
