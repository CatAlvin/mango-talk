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

### v0.4
Frontend prototype and core frontend-backend integration have been completed.

Completed frontend modules:
- Vue 3 + Vite frontend initialized
- Vue Router configured
- Pinia configured
- Axios request instance configured
- login page implemented
- protected chat page implemented
- auth bootstrap / session restore flow implemented
- `/auth/login` integrated
- `/users/me` integrated
- `/rooms/mine` integrated
- `/messages/room/{room_id}` integrated
- `/ws/rooms/{room_id}` integrated
- room list panel implemented
- message list panel implemented
- room switching behavior implemented
- WebSocket real-time receiving implemented
- WebSocket real-time sending implemented
- send failure feedback improved
- smart message auto-scroll behavior implemented
- basic responsive mobile adaptation implemented
- Nginx subdomain access for development environment implemented

Verified frontend workflows:
- access Mango Talk from `http://mango-talk.chenglan.tech`
- login with existing account
- restore current user via `/users/me`
- list joined rooms via `/rooms/mine`
- switch rooms in the chat UI
- load room history via `/messages/room/{room_id}`
- send real-time messages in current room via WebSocket
- receive real-time messages from another client in the same room
- keep message composer visible while message area scrolls independently
- basic mobile usage works without layout breaking

Current status:
- Mango Talk already supports **backend core chat capability + frontend interactive prototype**
- The project has entered the stage of **standard chat product prototype completion and incremental polish**

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
- image upload
- file upload
- message attachment model
- richer message rendering
- room avatar / user avatar support
- message recall event sync to frontend
- reply preview rendering
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
- Current project version is `v0.4`.
- Current public development domain is `mango-talk.chenglan.tech`.
- Existing blog deployment on `chenglan.tech` remains isolated from Mango Talk deployment.
- Current frontend prototype already supports login, room list, message list, and room-based real-time chat.
