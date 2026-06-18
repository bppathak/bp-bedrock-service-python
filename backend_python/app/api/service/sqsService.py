import os
from app.models.SQSModel import SQSRequest
from app.models.SQSModel import SQSResponse
from dotenv import load_dotenv

load_dotenv()
USE_SQS = os.getenv("USE_SQS")

def is_empty(value):
    return value.message is None or value.message.strip() == ""

def sendMessage(message: str):
    
    print(f"SQS service to: {message}")

    print(USE_SQS)
    if not USE_SQS:
        return f"Mock SQS response to: {message}"

    print(message)
    if is_empty(message):
        return SQSResponse(userResponse = "Not yet ready to send message to AWS SQS")

    #"Real SQS response"
    return SQSResponse(userResponse = "ready to send message to AWS SQS")

