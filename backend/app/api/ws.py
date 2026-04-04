import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_user_from_token
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.chat_room import ChatRoom
from app.models.chat_room_member import ChatRoomMember
from app.models.message import Message
from app.models.message_attachment import MessageAttachment
from app.services.ws_manager import manager

router = APIRouter(tags=["websocket"])


def get_room_member(db: Session, room_id: int, user_id: int) -> ChatRoomMember | None:
    return db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == user_id,
    ).first()


async def safe_send_personal_message(
    websocket: WebSocket,
    room_id: int,
    payload: dict,
) -> bool:
    try:
        await manager.send_personal_message(websocket, payload)
        return True
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        return False
    except RuntimeError:
        manager.disconnect(room_id, websocket)
        return False
    except Exception:
        manager.disconnect(room_id, websocket)
        return False


def serialize_attachment(attachment: MessageAttachment) -> dict:
    return {
        "id": attachment.id,
        "message_id": attachment.message_id,
        "attachment_type": attachment.attachment_type,
        "original_name": attachment.original_name,
        "stored_name": attachment.stored_name,
        "storage_path": attachment.storage_path,
        "file_url": attachment.file_url,
        "mime_type": attachment.mime_type,
        "file_size": attachment.file_size,
        "created_at": attachment.created_at.isoformat() if attachment.created_at else None,
    }


def serialize_message(message: Message, sender_username: str) -> dict:
    return {
        "id": message.id,
        "room_id": message.room_id,
        "sender_id": message.sender_id,
        "sender_username": sender_username,
        "message_type": message.message_type,
        "content": message.content,
        "reply_to_message_id": message.reply_to_message_id,
        "is_recalled": message.is_recalled,
        "recalled_at": message.recalled_at.isoformat() if message.recalled_at else None,
        "created_at": message.created_at.isoformat(),
        "attachments": [serialize_attachment(item) for item in message.attachments],
    }


def normalize_attachment_payload(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="附件数据格式错误")

    attachment_type = str(raw.get("attachment_type") or "").strip()
    original_name = str(raw.get("original_name") or "").strip()
    stored_name = str(raw.get("stored_name") or "").strip()
    storage_path = str(raw.get("storage_path") or "").strip()
    file_url = str(raw.get("file_url") or "").strip()
    mime_type = raw.get("mime_type")
    mime_type = str(mime_type).strip() if mime_type else None

    try:
        file_size = int(raw.get("file_size"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="附件大小不合法")

    if attachment_type not in {"image", "file"}:
        raise HTTPException(status_code=400, detail="附件类型不合法")

    if not original_name:
        raise HTTPException(status_code=400, detail="附件原始文件名不能为空")

    if not stored_name:
        raise HTTPException(status_code=400, detail="附件存储名不能为空")

    if not storage_path:
        raise HTTPException(status_code=400, detail="附件存储路径不能为空")

    if not file_url:
        raise HTTPException(status_code=400, detail="附件访问路径不能为空")

    if file_size <= 0:
        raise HTTPException(status_code=400, detail="附件大小必须大于 0")

    upload_root = os.path.abspath(settings.UPLOAD_ROOT)
    absolute_storage_path = os.path.abspath(storage_path)

    if absolute_storage_path != upload_root and not absolute_storage_path.startswith(upload_root + os.sep):
        raise HTTPException(status_code=400, detail="附件路径非法")

    if not os.path.exists(absolute_storage_path):
        raise HTTPException(status_code=400, detail=f"附件文件不存在：{original_name}")

    actual_stored_name = os.path.basename(absolute_storage_path)
    if actual_stored_name != stored_name:
        raise HTTPException(status_code=400, detail=f"附件存储名不匹配：{original_name}")

    actual_size = os.path.getsize(absolute_storage_path)
    if actual_size != file_size:
        raise HTTPException(status_code=400, detail=f"附件大小不匹配：{original_name}")

    if not file_url.startswith(f"{settings.UPLOAD_URL_PREFIX}/"):
        raise HTTPException(status_code=400, detail=f"附件访问路径非法：{original_name}")

    if not file_url.endswith(stored_name):
        raise HTTPException(status_code=400, detail=f"附件访问路径与存储名不匹配：{original_name}")

    return {
        "attachment_type": attachment_type,
        "original_name": original_name,
        "stored_name": stored_name,
        "storage_path": absolute_storage_path,
        "file_url": file_url,
        "mime_type": mime_type,
        "file_size": file_size,
    }


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room_chat(websocket: WebSocket, room_id: int):
    token = websocket.query_params.get("token")

    db = SessionLocal()
    try:
        try:
            current_user = get_user_from_token(token, db)
        except HTTPException:
            await websocket.close(code=1008)
            return

        room = db.get(ChatRoom, room_id)
        if not room or not room.is_active:
            await websocket.close(code=1008)
            return

        membership = get_room_member(db, room_id, current_user.id)
        if not membership:
            await websocket.close(code=1008)
            return

        await manager.connect(room_id, websocket)

        connected_ok = await safe_send_personal_message(
            websocket,
            room_id,
            {
                "event": "connected",
                "data": {
                    "room_id": room_id,
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "online_count": manager.room_connection_count(room_id),
                },
            },
        )
        if not connected_ok:
            return

    finally:
        db.close()

    try:
        while True:
            try:
                payload = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except RuntimeError as exc:
                if "WebSocket is not connected" in str(exc):
                    break
                raise

            action = payload.get("action")
            data = payload.get("data") or {}

            if not isinstance(data, dict):
                ok = await safe_send_personal_message(
                    websocket,
                    room_id,
                    {
                        "event": "error",
                        "data": {"message": "invalid data payload"},
                    },
                )
                if not ok:
                    break
                continue

            if action == "ping":
                pong_ok = await safe_send_personal_message(
                    websocket,
                    room_id,
                    {
                        "event": "pong",
                        "data": {
                            "room_id": room_id,
                            "ts": datetime.now(timezone.utc).isoformat(),
                        },
                    },
                )
                if not pong_ok:
                    break
                continue

            if action != "send_message":
                ok = await safe_send_personal_message(
                    websocket,
                    room_id,
                    {
                        "event": "error",
                        "data": {
                            "message": "unsupported action",
                        },
                    },
                )
                if not ok:
                    break
                continue

            db = SessionLocal()
            try:
                room = db.get(ChatRoom, room_id)
                if not room or not room.is_active:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "room not available"},
                        },
                    )
                    if not ok:
                        break
                    continue

                membership = get_room_member(db, room_id, current_user.id)
                if not membership:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "you are not in this room"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if membership.is_muted:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "you are muted"},
                        },
                    )
                    if not ok:
                        break
                    continue

                message_type = str(data.get("message_type") or "text").strip().lower()
                content = (data.get("content") or "").strip()
                raw_attachments = data.get("attachments") or []
                reply_to_message_id = data.get("reply_to_message_id")

                if message_type not in {"text", "image", "file"}:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "unsupported message_type"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if not isinstance(raw_attachments, list):
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "attachments must be a list"},
                        },
                    )
                    if not ok:
                        break
                    continue

                attachments = []
                try:
                    attachments = [normalize_attachment_payload(item) for item in raw_attachments]
                except HTTPException as exc:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": exc.detail},
                        },
                    )
                    if not ok:
                        break
                    continue

                if message_type == "text" and not content:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "content cannot be empty"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if message_type in {"image", "file"} and not attachments:
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "attachment message requires attachments"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if message_type == "image" and any(item["attachment_type"] != "image" for item in attachments):
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "image message can only contain image attachments"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if message_type == "file" and any(item["attachment_type"] != "file" for item in attachments):
                    ok = await safe_send_personal_message(
                        websocket,
                        room_id,
                        {
                            "event": "error",
                            "data": {"message": "file message can only contain file attachments"},
                        },
                    )
                    if not ok:
                        break
                    continue

                if reply_to_message_id is not None:
                    try:
                        reply_to_message_id = int(reply_to_message_id)
                    except (TypeError, ValueError):
                        ok = await safe_send_personal_message(
                            websocket,
                            room_id,
                            {
                                "event": "error",
                                "data": {"message": "reply_to_message_id is invalid"},
                            },
                        )
                        if not ok:
                            break
                        continue

                    reply_target = db.get(Message, reply_to_message_id)
                    if not reply_target:
                        ok = await safe_send_personal_message(
                            websocket,
                            room_id,
                            {
                                "event": "error",
                                "data": {"message": "reply target not found"},
                            },
                        )
                        if not ok:
                            break
                        continue

                    if reply_target.room_id != room_id:
                        ok = await safe_send_personal_message(
                            websocket,
                            room_id,
                            {
                                "event": "error",
                                "data": {"message": "reply target is in another room"},
                            },
                        )
                        if not ok:
                            break
                        continue

                msg = Message(
                    room_id=room_id,
                    sender_id=current_user.id,
                    message_type=message_type,
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
                            attachment_type=attachment["attachment_type"],
                            original_name=attachment["original_name"],
                            stored_name=attachment["stored_name"],
                            storage_path=attachment["storage_path"],
                            file_url=attachment["file_url"],
                            mime_type=attachment["mime_type"],
                            file_size=attachment["file_size"],
                        )
                    )

                db.commit()

                message_with_attachments = db.execute(
                    select(Message)
                    .options(selectinload(Message.attachments))
                    .where(Message.id == msg.id)
                ).scalar_one()

                outgoing = {
                    "event": "new_message",
                    "data": serialize_message(message_with_attachments, current_user.username),
                }

            finally:
                db.close()

            await manager.broadcast(room_id, outgoing)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room_id, websocket)