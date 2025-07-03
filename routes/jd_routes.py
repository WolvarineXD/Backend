from fastapi import APIRouter, HTTPException, Depends, Security, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.jd_model import JDInput
from utils import decode_access_token
from db import jd_collection
from bson import ObjectId
import httpx

router = APIRouter(prefix="/jd", tags=["JD"])
security = HTTPBearer()
AI_ENDPOINT = "https://n8n-resume-ai.onrender.com/webhook-test/a109fa4f-8418-4887-8583-1b6f03149cac"

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
        "skills": jd.skills,
        "resume_drive_link": jd.resume_drive_link
    }

    result = await jd_collection.insert_one(jd_doc)
    jd_id = str(result.inserted_id)

    # ✅ Send to AI
    try:
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(AI_ENDPOINT, json={
                "jd_id": jd_id,
                "job_title": jd.job_title,
                "job_description": jd.job_description,
                "skills": jd.skills,
                "resume_drive_link": jd.resume_drive_link
            })
            if ai_response.status_code != 200:
                raise Exception(f"AI Error: {ai_response.text}")
    except Exception as e:
        print(f"⚠️ AI processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process JD with AI")

    return {"message": "JD saved successfully and sent to AI", "jd_id": jd_id}




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
            "skills": jd["skills"],
            "resume_drive_link": jd.get("resume_drive_link")
            
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
                "skills": updated_data.skills,
                "resume_drive_link": updated_data.resume_drive_link  # ✅ added
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="JD not found or no changes made")

    return {"message": "JD updated successfully"}


@router.delete("/delete/{jd_id}")
async def delete_jd(
    jd_id: str = Path(..., description="JD ID to delete"),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await jd_collection.delete_one({
        "_id": ObjectId(jd_id),
        "user_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="JD not found")

    return {"message": "JD deleted successfully"}
