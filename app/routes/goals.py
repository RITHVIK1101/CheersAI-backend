from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.models import Goal
from app.database import goals_collection

router = APIRouter()

@router.post("/home")
async def create_goal(goal: Goal):
    goal_doc = goal.dict()
    goal_doc["user_id"] = "guest"
    goals_collection.insert_one(goal_doc)
    return {"message": "Goal created successfully"}

@router.get("/home", response_model=list[Goal])
async def get_goals():
    goals = goals_collection.find({"user_id": "guest"})
    return list(goals)

@router.put("/home/{goal_id}")
async def update_goal(goal_id: str, goal: Goal):
    update_result = goals_collection.update_one(
        {"_id": ObjectId(goal_id), "user_id": "guest"},
        {"$set": goal.dict()}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal updated successfully"}

@router.delete("/home/{goal_id}")
async def delete_goal(goal_id: str):
    delete_result = goals_collection.delete_one({"_id": ObjectId(goal_id), "user_id": "guest"})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted successfully"}
