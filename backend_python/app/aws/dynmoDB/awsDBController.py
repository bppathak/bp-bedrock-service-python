from fastapi import APIRouter
import aws_controller

router = APIRouter()

@router.get("/get-items")
def get_items():
    return aws_controller.get_items()