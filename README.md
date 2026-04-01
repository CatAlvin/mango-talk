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
- WebSocket (planned for chat real-time messaging)

### Database / Storage
- MySQL 8
- Local file storage on Ubuntu server

### Deployment
- Ubuntu 22.04
- Nginx
- systemd
- GitHub for version control

## Current Progress

### v0.1
Backend authentication foundation has been completed:
- FastAPI project initialized
- MySQL connection established
- Health check endpoints created
- User model created
- User registration implemented
- User login implemented
- JWT token issuing implemented
- `/users/me` authenticated endpoint implemented

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

## Roadmap

### Next
- Chat room data model
- Room membership model
- Message model
- WebSocket-based real-time messaging
- Message history API
- Vue frontend initialization
- Nginx reverse proxy for chat subdomain
- HTTPS support
- File upload support
- Admin moderation features

### Notes
- Secrets must never be committed.
- backend/.env is local-only.
- Frontend initialization has not started yet.
- Current version is backend-first.