from fastapi import APIRouter, HTTPException, Depends, status
import instaloader
from datetime import datetime, timezone
from bson import ObjectId

from ..models import ManualScanRequest, AutoScanRequest, ScanResponse
from ..auth import get_current_user
from ..database import db
from ..ml.predictor import extract_features, run_prediction

router = APIRouter(prefix="/api/scan", tags=["scan"])

# Shared logic to save scan result to user history
async def save_to_history(user_id: ObjectId, username: str, type_str: str, is_fake: bool, probability: float, is_verified: bool, features: dict):
    history_record = {
        "user_id": user_id,
        "username": username,
        "type": type_str,
        "is_fake": is_fake,
        "probability": probability,
        "is_verified": is_verified,
        "scanned_at": datetime.now(timezone.utc),
        "features": features
    }
    await db.history.insert_one(history_record)

@router.post("/manual", response_model=ScanResponse)
async def scan_manual(req: ManualScanRequest, current_user: dict = Depends(get_current_user)):
    username = req.username.strip()
    fullname = req.fullname.strip()
    
    # Validation
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
    if not fullname:
        raise HTTPException(status_code=400, detail="Full Name is required.")

    # 1. Blue Tick Bypassing
    if req.is_verified:
        is_fake = False
        probability = 0.0
    else:
        # 2. Feature engineering & prediction
        try:
            features_mat = extract_features(
                username=username,
                fullname=fullname,
                bio_input=req.bio_input,
                has_url=req.has_url,
                is_private=req.is_private,
                has_pic=req.has_pic,
                posts=req.posts,
                followers=req.followers,
                follows=req.follows
            )
            is_fake, probability = run_prediction(features_mat)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    # Features dict to store/return for UI comparison
    features_dict = {
        "fullname": fullname,
        "bio_input": req.bio_input,
        "posts": req.posts,
        "followers": req.followers,
        "follows": req.follows,
        "has_pic": req.has_pic,
        "is_private": req.is_private,
        "has_url": req.has_url
    }

    # Save to history
    await save_to_history(
        user_id=current_user["_id"],
        username=username,
        type_str="manual",
        is_fake=is_fake,
        probability=probability,
        is_verified=req.is_verified,
        features=features_dict
    )

    return ScanResponse(
        username=username,
        is_fake=is_fake,
        probability=probability,
        is_verified=req.is_verified,
        features=features_dict
    )


@router.post("/auto", response_model=ScanResponse)
async def scan_auto(req: AutoScanRequest, current_user: dict = Depends(get_current_user)):
    target_username = req.username.strip()
    if not target_username:
        raise HTTPException(status_code=400, detail="Username is required.")

    # 1. Fetch data from Instaloader
    try:
        L = instaloader.Instaloader()
        # Fetch profile
        profile = instaloader.Profile.from_username(L.context, target_username)
        
        # Prepare parameters
        i_username = profile.username
        i_fullname = profile.full_name if profile.full_name else ""
        i_bio = profile.biography if profile.biography else ""
        i_has_url = bool(profile.external_url)
        i_is_private = profile.is_private
        i_has_pic = bool(profile.profile_pic_url)
        i_is_verified = profile.is_verified
        i_posts = profile.mediacount
        i_followers = profile.followers
        i_follows = profile.followees
        
    except instaloader.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail="Instagram profile does not exist.")
    except instaloader.ConnectionException:
        raise HTTPException(status_code=503, detail="Connection Error: Instagram refused the connection. Try again later or use Manual Entry.")
    except instaloader.LoginRequiredException:
        raise HTTPException(status_code=403, detail="Login Error: Instagram requires login to view this profile. Please use Manual Entry.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Instaloader error: {str(e)}")

    # 2. Prediction
    if i_is_verified:
        is_fake = False
        probability = 0.0
    else:
        try:
            features_mat = extract_features(
                username=i_username,
                fullname=i_fullname,
                bio_input=i_bio,
                has_url=i_has_url,
                is_private=i_is_private,
                has_pic=i_has_pic,
                posts=i_posts,
                followers=i_followers,
                follows=i_follows
            )
            is_fake, probability = run_prediction(features_mat)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    features_dict = {
        "fullname": i_fullname,
        "bio_input": i_bio,
        "posts": i_posts,
        "followers": i_followers,
        "follows": i_follows,
        "has_pic": i_has_pic,
        "is_private": i_is_private,
        "has_url": i_has_url
    }

    # Save to history
    await save_to_history(
        user_id=current_user["_id"],
        username=i_username,
        type_str="auto",
        is_fake=is_fake,
        probability=probability,
        is_verified=i_is_verified,
        features=features_dict
    )

    return ScanResponse(
        username=i_username,
        is_fake=is_fake,
        probability=probability,
        is_verified=i_is_verified,
        features=features_dict
    )
