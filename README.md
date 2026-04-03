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
- Element Plus (for selected UI components)

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

### v0.3
Backend core chat architecture has been completed.

Completed modules:
- FastAPI backend foundation
- MySQL connection and database initialization
- Health check endpoints
- User registration
- User login
- JWT-based authentication
- Protected current-user endpoint (`/users/me`)
- Chat room data model
- Private room creation
- Group room creation
- My room list endpoint
- Message data model
- Send text message endpoint
- Room message history endpoint
- Reply-to-message support
- Recall message endpoint
- WebSocket room-based real-time messaging architecture
- Connection manager for room-level broadcast
- WebSocket token-based authentication design
- WebSocket test scripts

Verified backend workflows:
- register user
- login user
- obtain JWT token
- identify current user with token
- create private room
- create group room
- list joined rooms
- send text message in room
- reply to an existing message
- fetch room message history
- recall own message

Current status:
- Mango Talk backend already supports **authentication, rooms, messages, and real-time communication architecture**
- The project is ready to move into the **Vue frontend initialization and integration stage**

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

!!!bash
cd /home/projects/mango-talk/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
!!!

## Roadmap

### v0.4 — Frontend Initialization
- initialize Vue 3 + Vite frontend
- configure Vue Router
- configure Pinia
- build login page
- build chat layout
- build room list panel
- build message list panel
- connect frontend auth flow with backend JWT
- connect frontend room APIs and message APIs
- connect frontend WebSocket chat flow

### v0.5 — Richer Chat Features
- image upload
- file upload
- message attachment model
- richer message rendering
- room avatar / user avatar support
- message recall event sync to frontend
- reply preview rendering
- basic online state and typing indicator planning

### v0.6 — Deployment and Production Hardening
- configure Mango Talk subdomain
- Nginx reverse proxy for backend and frontend
- systemd service for backend
- HTTPS with Certbot
- environment cleanup and production configuration
- logging improvements
- production validation

## Notes

- Secrets must never be committed.
- `backend/.env` is local-only.
- Frontend initialization has not started yet.
- Current backend version is `v0.3`.
- Existing blog deployment on `chenglan.tech` should remain isolated from Mango Talk deployment.
- Recommended future subdomain:
  - `talk.chenglan.tech`
  - or `mango-talk.chenglan.tech`