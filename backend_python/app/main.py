from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter
from app.service import sqsService as sqsService
from app.models.SQSModel import SQSRequest

router = APIRouter(prefix="/sqs")

app = FastAPI(title = "AWS Bedrock Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


@app.post("/health")
def healthCheck():
    return {"status":"Service running ok"}

@app.post("/sendMessage")
def sendMessage(sqsRequest : SQSRequest):
    print(" ++++++ {sqsRequest.message}")
    return sqsService.sendMessage(sqsRequest)
