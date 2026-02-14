from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status

from src.firerisk.api.databases.postgres.models import Users
from src.firerisk.api.routers.auth import get_current_user
from src.firerisk.api.databases.postgres.database import POSTGRES_SessionLocal


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = POSTGRES_SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/users", status_code=status.HTTP_200_OK)
async def see_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail='Forbidden: Admins only')
    return db.query(Users).all()


@router.delete("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, 
                      db: db_dependency,
                      username: str = Path(..., description="The username of the user to delete"), ):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail='Forbidden: Admins only')
    
    user_to_delete = db.query(Users).filter(Users.username == username).first()
    if user_to_delete is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    if user_to_delete.role == "admin":
        raise HTTPException(status_code=403, detail='Forbidden: Cannot delete admin users')
    
    db.delete(user_to_delete)
    db.commit()