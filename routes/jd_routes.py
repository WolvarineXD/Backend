from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.jd_model import JDInput
from utils import decode_access_token
from db import jd_collection
from bson import ObjectId

router = APIRouter(prefix="/jd", tags=["JD"])
security = HTTPBearer()

@router.post("/submit")
async def submit_jd(
    jd: JDInput,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    jd_doc = {
        "user_id": ObjectId(user_id),
        "job_title": jd.job_title,
        "job_description": jd.job_description,
        "skills": jd.skills
    }

    result = await jd_collection.insert_one(jd_doc)
    return {"message": "JD saved successfully", "jd_id": str(result.inserted_id)}

# ✅ NEW: Get all JDs for the logged-in user
@router.get("/history")
async def get_jd_history(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    history = []
    cursor = jd_collection.find({"user_id": ObjectId(user_id)})
    async for jd in cursor:
        history.append({
            "jd_id": str(jd["_id"]),
            "job_title": jd["job_title"],
            "job_description": jd["job_description"],
            "skills": jd["skills"]
        })

    return {"history": history}
@router.put("/update/{jd_id}")
async def update_jd(
    jd_id: str,
    updated_data: JDInput,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    result = await jd_collection.update_one(
        {
            "_id": ObjectId(jd_id),
            "user_id": ObjectId(user_id)
        },
        {
            "$set": {
                "job_title": updated_data.job_title,
                "job_description": updated_data.job_description,
                "skills": updated_data.skills
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="JD not found or no changes made")

    return {"message": "JD updated successfully"}
