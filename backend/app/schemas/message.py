from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MessageAttachmentCreate(BaseModel):
    attachment_type: str = Field(min_length=1, max_length=20)
    original_name: str = Field(min_length=1, max_length=255)
    stored_name: str = Field(min_length=1, max_length=255)
    storage_path: str = Field(min_length=1, max_length=500)
    file_url: str = Field(min_length=1, max_length=500)
    mime_type: str | None = Field(default=None, max_length=100)
    file_size: int = Field(gt=0)


class MessageAttachmentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_id: int
    attachment_type: str
    original_name: str
    stored_name: str
    storage_path: str
    file_url: str
    mime_type: str | None
    file_size: int
    created_at: datetime


class MessageCreate(BaseModel):
    room_id: int = Field(gt=0)
    message_type: str = Field(default="text", max_length=20)
    content: str | None = None
    reply_to_message_id: int | None = Field(default=None, gt=0)
    attachments: list[MessageAttachmentCreate] = Field(default_factory=list)


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
    attachments: list[MessageAttachmentPublic] = Field(default_factory=list)


class MessageActionResponse(BaseModel):
    message: str
    data: MessagePublic