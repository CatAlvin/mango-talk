from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class MessageCreate(BaseModel):
    room_id: int = Field(gt=0)
    message_type: str = Field(default="text", max_length=20)
    content: str | None = None
    reply_to_message_id: int | None = Field(default=None, gt=0)

class MessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    sender_id: int
    message_type: str
    content: str | None
    reply_to_message_id: int | None
    is_recalled: bool
    recalled_at: datetime | None
    created_at: datetime

class MessageActionResponse(BaseModel):
    message: str
    data: MessagePublic
