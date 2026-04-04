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

### v0.5
Mango Talk has entered the stage of **richer chat features and more product-like message interaction**.

Completed backend / frontend capabilities:
- upload API `/uploads` completed
- local disk file storage path works
- `message_attachments` table and model completed
- attachment metadata can be linked to messages
- `/messages` now supports `text / image / file`
- `/messages/room/{room_id}` now returns attachments with messages
- attachment messages can be sent through WebSocket
- attachment messages can be broadcast in real time
- frontend supports richer attachment rendering
- file messages render as attachment cards
- image messages render as image previews
- frontend upload entry added in chat composer
- frontend now supports upload -> send attachment message workflow
- public subdomain upload routing works through Nginx
- recall button added for own messages
- recall action now syncs to all clients through WebSocket event
- recall state updates in real time without manual refresh

Verified workflows:
- upload a file from the chat composer
- backend saves uploaded file to local disk
- upload metadata is returned successfully
- frontend sends uploaded attachment as `file` or `image` message
- current room receives the attachment message in real time
- historical message list still shows attachment content after refresh
- own message can be recalled from frontend
- other clients in the same room receive recall updates in real time

Current status:
- Mango Talk already supports **text chat + attachment chat + real-time recall sync**
- the project has moved beyond a plain chat prototype and is now much closer to a usable standard chat product

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

### v0.5 — Richer Chat Features
Completed:
- image upload foundation
- file upload foundation
- message attachment model
- richer message rendering
- frontend upload entry
- message recall event sync to frontend

Still to do:
- room avatar support
- user avatar upload / display support
- reply preview rendering upgrade
- room creation entry in frontend
- better mobile interaction polish

### v0.6 — Deployment and Production Hardening
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
- Current project version is `v0.5`.
- Current public development domain is `mango-talk.chenglan.tech`.
- Existing blog deployment on `chenglan.tech` remains isolated from Mango Talk deployment.
- Current Mango Talk prototype already supports login, room list, message list, room-based real-time chat, attachment messages, and real-time recall sync.