from fastapi import APIRouter
# Global ban logic has been removed as per requirements.
# This file is kept empty or minimal to avoid import errors if referenced, 
# or we can just have a placeholder.

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def list_users():
    return {"message": "User management is handled via Auth and Room logic."}
