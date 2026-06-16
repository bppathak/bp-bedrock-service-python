from pydantic import BaseModel

class SQSRequest(BaseModel):
    message : str

class SQSResponse(BaseModel):
    userResponse : str