from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.deps import get_db
from app.models.chat_room import ChatRoom
from app.models.chat_room_member import ChatRoomMember
from app.models.message import Message
from app.models.message_attachment import MessageAttachment
from app.models.user import User
from app.schemas.message import (
    MessageAttachmentCreate,
    MessageActionResponse,
    MessageCreate,
    MessagePublic,
)
from app.services.ws_manager import manager

router = APIRouter(prefix="/messages", tags=["messages"])


def get_room_member(db: Session, room_id: int, user_id: int) -> ChatRoomMember | None:
    return db.execute(
        select(ChatRoomMember).where(
            ChatRoomMember.room_id == room_id,
            ChatRoomMember.user_id == user_id,
        )
    ).scalar_one_or_none()


def validate_attachment_payload(attachment: MessageAttachmentCreate) -> None:
    if attachment.attachment_type not in {"image", "file"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="附件类型不合法",
        )

    upload_root = os.path.abspath(settings.UPLOAD_ROOT)
    storage_path = os.path.abspath(attachment.storage_path)

    if storage_path != upload_root and not storage_path.startswith(upload_root + os.sep):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="附件路径非法",
        )

    if not os.path.exists(storage_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"附件文件不存在：{attachment.original_name}",
        )

    actual_stored_name = os.path.basename(storage_path)
    if actual_stored_name != attachment.stored_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"附件存储名不匹配：{attachment.original_name}",
        )

    actual_size = os.path.getsize(storage_path)
    if actual_size != attachment.file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"附件大小不匹配：{attachment.original_name}",
        )

    if not attachment.file_url.startswith(f"{settings.UPLOAD_URL_PREFIX}/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"附件访问路径非法：{attachment.original_name}",
        )

    if not attachment.file_url.endswith(attachment.stored_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"附件访问路径与存储名不匹配：{attachment.original_name}",
        )


@router.post("", response_model=MessageActionResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.get(ChatRoom, payload.room_id)
    if not room or not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="房间不存在或不可用",
        )

    membership = get_room_member(db, payload.room_id, current_user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不在该房间内",
        )

    if membership.is_muted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你已被禁言，无法发送消息",
        )

    if payload.message_type not in {"text", "image", "file"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前阶段仅支持 text / image / file 消息",
        )

    content = (payload.content or "").strip()
    attachments = payload.attachments or []

    if payload.message_type == "text" and not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本消息内容不能为空",
        )

    if payload.message_type in {"image", "file"} and not attachments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="附件消息必须至少带一个附件",
        )

    if payload.message_type == "image":
        if any(item.attachment_type != "image" for item in attachments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image 消息只能携带图片附件",
            )

    if payload.message_type == "file":
        if any(item.attachment_type != "file" for item in attachments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file 消息只能携带普通文件附件",
            )

    reply_to_message_id = payload.reply_to_message_id
    if reply_to_message_id is not None:
        reply_target = db.get(Message, reply_to_message_id)
        if not reply_target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="被回复的消息不存在",
            )
        if reply_target.room_id != payload.room_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能回复其他房间的消息",
            )

    for attachment in attachments:
        validate_attachment_payload(attachment)

    msg = Message(
        room_id=payload.room_id,
        sender_id=current_user.id,
        message_type=payload.message_type,
        content=content or None,
        reply_to_message_id=reply_to_message_id,
        is_recalled=False,
    )
    db.add(msg)
    db.flush()

    for attachment in attachments:
        db.add(
            MessageAttachment(
                message_id=msg.id,
                attachment_type=attachment.attachment_type,
                original_name=attachment.original_name,
                stored_name=attachment.stored_name,
                storage_path=attachment.storage_path,
                file_url=attachment.file_url,
                mime_type=attachment.mime_type,
                file_size=attachment.file_size,
            )
        )

    db.commit()

    message_with_attachments = db.execute(
        select(Message)
        .options(selectinload(Message.attachments))
        .where(Message.id == msg.id)
    ).scalar_one()

    return {
        "message": "message sent",
        "data": message_with_attachments,
    }


@router.get("/room/{room_id}", response_model=list[MessagePublic])
def list_room_messages(
    room_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.get(ChatRoom, room_id)
    if not room or not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="房间不存在或不可用",
        )

    membership = get_room_member(db, room_id, current_user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不在该房间内",
        )

    messages = db.execute(
        select(Message)
        .options(selectinload(Message.attachments))
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(limit)
    ).scalars().all()

    return messages


@router.post("/{message_id}/recall", response_model=MessageActionResponse)
async def recall_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.execute(
        select(Message)
        .options(selectinload(Message.attachments))
        .where(Message.id == message_id)
    ).scalar_one_or_none()

    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在",
        )

    membership = get_room_member(db, msg.room_id, current_user.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不在该房间内",
        )

    if msg.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能撤回自己发送的消息",
        )

    if msg.is_recalled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该消息已经撤回",
        )

    msg.is_recalled = True
    msg.recalled_at = datetime.now()
    db.commit()
    db.refresh(msg)

    await manager.broadcast(
        msg.room_id,
        {
            "event": "message_recalled",
            "data": {
                "id": msg.id,
                "room_id": msg.room_id,
                "sender_id": msg.sender_id,
                "is_recalled": True,
                "recalled_at": msg.recalled_at.isoformat() if msg.recalled_at else None,
            },
        },
    )

    return {
        "message": "message recalled",
        "data": msg,
    }