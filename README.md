# Mango Talk

Mango Talk is a standard real-time chat web application designed for small teams and campus/community communication.  
The project focuses on clean architecture, practical deployment on Ubuntu, good UI potential, and future extensibility.

## Project Positioning

This is **not** a simple demo and **not** a full Discord/Slack clone.  
It is positioned as a **standard chat system** with a clear engineering structure and real deployment value.

Target capabilities:
- User registration and login
- JWT-based authentication
- One-to-one chat
- Group chat
- Persistent message storage
- Real-time WebSocket messaging
- Image and file upload
- Admin moderation features
- Ubuntu server deployment with Nginx

## Tech Stack

### Frontend
- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- SCSS
- Element Plus（selected use only）

### Backend
- Python 3.10
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- python-dotenv
- passlib + bcrypt
- python-jose
- WebSocket

### Database / Storage
- MySQL 8
- Local file storage on Ubuntu server

### Deployment
- Ubuntu 22.04
- Nginx
- systemd
- GitHub for version control

## Current Progress

### v0.6
Mango Talk has entered the stage of **room creation completion and full reply interaction polish**.

Completed backend / frontend capabilities:
- frontend private room creation entry completed
- frontend group room creation entry completed
- `/users/search` added for user lookup in room creation workflow
- frontend can now search users and directly create or enter existing private rooms
- frontend can now create group rooms with group name, optional description, and member selection
- room list refresh + auto-enter after room creation completed
- reply preview UI upgraded from simple `reply_to_message_id` hint to readable preview block
- reply action entry added on message cards
- composer now supports “replying to message” state
- text message sending now carries `reply_to_message_id`
- attachment message sending now also carries `reply_to_message_id`
- desktop message action buttons are now hover-revealed for cleaner UI
- mobile message action buttons remain visible for usability
- reply preview is clickable and can jump to the original message
- jumped target message now gets temporary highlight feedback
- backend message schema now returns `sender_username`
- backend message schema now returns `replied_message` preview payload
- `/messages/room/{room_id}` now returns reply preview summary for reply messages
- WebSocket `new_message` payload now also returns reply preview summary
- frontend reply preview now prefers backend `replied_message` instead of relying only on currently loaded messages

Verified workflows:
- search users from frontend and create private room successfully
- create group room from frontend and auto-enter the new room successfully
- reply to an existing message from frontend composer successfully
- send text reply message with correct reply relation successfully
- send attachment reply message with correct reply relation successfully
- click reply preview and jump back to the original message successfully
- original message highlight feedback works after jump
- reply preview remains readable even when the original message is not currently in the latest loaded list, as long as backend returns `replied_message`

Current status:
- Mango Talk already supports **text chat + attachment chat + real-time recall sync + frontend room creation + usable reply workflow**
- the project has moved beyond a plain real-time chat prototype and is now much closer to a complete standard chat product

## Project Structure

```text
mango-talk/
├── backend/
├── frontend/
├── uploads/
├── logs/
├── backups/
├── scripts/
└── docs/
```

## Run Backend Locally on Server

```bash
cd /home/projects/mango-talk/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Run Frontend Locally on Server

```bash
cd /home/projects/mango-talk/frontend
npm run dev
```

## Roadmap

### v0.6 — Room Creation and Reply Workflow Polish
Completed:
- frontend private room creation entry
- frontend group room creation entry
- user search endpoint for room creation
- reply preview rendering upgrade
- frontend reply action entry
- composer reply state
- clickable reply preview jump-to-origin interaction
- reply preview backend summary payload
- cleaner desktop message action interaction
- better mobile action visibility

### v0.7 — Profile System and Product Polish
Planned:
- room avatar support
- user avatar upload / display support
- user profile edit page
- personal information update
- password change
- avatar upload for user profile
- richer room header presentation
- better mobile interaction polish for room creation and message actions
- overall UI polish for profile-related interaction

### v0.8 — Deployment and Production Hardening
Planned:
- replace Vite dev serving with production frontend build
- Nginx serve frontend static files directly
- stable reverse proxy for backend REST API and WebSocket
- systemd service for backend
- HTTPS with Certbot
- environment cleanup and production configuration
- logging improvements
- production validation

## Notes

- Secrets must never be committed.
- `backend/.env` is local-only.
- Current project version is `v0.6`.
- Current public development domain is `mango-talk.chenglan.tech`.
- Existing blog deployment on `chenglan.tech` remains isolated from Mango Talk deployment.
- Current Mango Talk prototype already supports login, room list, message list, room-based real-time chat, attachment messages, real-time recall sync, frontend room creation, and full basic reply interaction.