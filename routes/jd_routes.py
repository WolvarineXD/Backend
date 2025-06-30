from datetime import datetime
from fastapi import APIRouter, HTTPException, Security, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from bson import ObjectId
from bson.errors import InvalidId
from typing import Dict, Optional

router = APIRouter(prefix="/jd", tags=["JD"])
security = HTTPBearer()

# Utility function for ObjectId validation
def validate_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# Request/Response Models
class JDInput(BaseModel):
    job_title: str
    job_description: str
    skills: Dict[str, int]

class JDResponse(BaseModel):
    message: str
    jd_id: Optional[str] = None

class JDSingleResponse(BaseModel):
    jd_id: str
    job_title: str
    job_description: str
    skills: Dict[str, int]
    created_at: datetime

class JDHistoryResponse(BaseModel):
    history: list[JDSingleResponse]

# Routes
@router.post("/submit", response_model=JDResponse)
async def submit_jd(
    jd: JDInput,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Submit a new job description"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        jd_doc = {
            "user_id": ObjectId(user_id),
            "job_title": jd.job_title,
            "job_description": jd.job_description,
            "skills": jd.skills,
            "created_at": datetime.utcnow()
        }

        result = await jd_collection.insert_one(jd_doc)
        return {"message": "JD saved successfully", "jd_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save JD: {str(e)}")

@router.get("/{jd_id}", response_model=JDSingleResponse)
async def get_jd(
    jd_id: str = Path(..., description="JD ID to fetch"),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get a single job description by ID"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        obj_id = validate_object_id(jd_id)
        jd = await jd_collection.find_one({
            "_id": obj_id,
            "user_id": ObjectId(user_id)
        })

        if not jd:
            raise HTTPException(status_code=404, detail="JD not found")

        return {
            "jd_id": str(jd["_id"]),
            "job_title": jd["job_title"],
            "job_description": jd["job_description"],
            "skills": jd["skills"],
            "created_at": jd["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch JD: {str(e)}")

@router.get("/history", response_model=JDHistoryResponse)
async def get_jd_history(
    skip: int = 0,
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get user's job description history with pagination"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        history = []
        cursor = jd_collection.find(
            {"user_id": ObjectId(user_id)}
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        async for jd in cursor:
            history.append({
                "jd_id": str(jd["_id"]),
                "job_title": jd["job_title"],
                "job_description": jd["job_description"],
                "skills": jd["skills"],
                "created_at": jd["created_at"]
            })

        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.put("/update/{jd_id}", response_model=JDResponse)
async def update_jd(
    jd_id: str,
    updated_data: JDInput,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Update an existing job description"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    try:
        obj_id = validate_object_id(jd_id)
        result = await jd_collection.update_one(
            {
                "_id": obj_id,
                "user_id": ObjectId(user_id)
            },
            {
                "$set": {
                    "job_title": updated_data.job_title,
                    "job_description": updated_data.job_description,
                    "skills": updated_data.skills,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="JD not found or no changes made")

        return {"message": "JD updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update JD: {str(e)}")

@router.delete("/delete/{jd_id}", response_model=JDResponse)
async def delete_jd(
    jd_id: str = Path(..., description="JD ID to delete"),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Delete a job description"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        obj_id = validate_object_id(jd_id)
        result = await jd_collection.delete_one({
            "_id": obj_id,
            "user_id": ObjectId(user_id)
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="JD not found")

        return {"message": "JD deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete JD: {str(e)}")
