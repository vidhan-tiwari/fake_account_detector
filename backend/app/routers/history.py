from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from typing import List

from ..models import HistoryResponse
from ..auth import get_current_user
from ..database import db

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("", response_model=List[HistoryResponse])
async def get_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    
    # Retrieve user's scan history sorted by date descending
    cursor = db.history.find({"user_id": user_id}).sort("scanned_at", -1)
    
    history_list = []
    async for doc in cursor:
        history_list.append(
            HistoryResponse(
                id=str(doc["_id"]),
                username=doc["username"],
                type=doc["type"],
                is_fake=doc["is_fake"],
                probability=doc["probability"],
                is_verified=doc["is_verified"],
                scanned_at=doc["scanned_at"],
                features=doc.get("features", {})
            )
        )
    return history_list

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_record(record_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]
    
    try:
        obj_id = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid record ID format.")
        
    # Find and delete only if it belongs to the current user
    result = await db.history.delete_one({"_id": obj_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found or access denied."
        )
        
    return
