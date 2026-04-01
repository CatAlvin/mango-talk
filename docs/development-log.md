# Mango Talk Development Log

---

## Version 0.1 — 2026-04-02

### Project Stage
Backend foundation completed.  
The project has moved from environment setup to initial business capability.

### Confirmed Project Positioning
Mango Talk is a standard chat web application for:
- small teams
- friends
- campus / student organization communication

This project is intended to be:
- practical
- deployable on Ubuntu
- visually presentable later
- extensible in future iterations

### Confirmed Tech Stack

#### Frontend
- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- SCSS
- Element Plus (partial use)

#### Backend
- Python 3.10
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- python-dotenv
- passlib
- bcrypt
- python-jose
- WebSocket (planned)

#### Infrastructure
- Ubuntu 22.04
- Nginx
- MySQL 8
- systemd
- GitHub

---

### Server Environment Notes
Confirmed environment:
- Ubuntu 22.04.5 LTS
- 2 vCPU
- 3.5 GiB memory
- 40 GB disk
- Nginx active
- MySQL active

Important environment adjustments already completed:
- exited Conda base environment
- switched to system Python: `/usr/bin/python3`
- confirmed Python version: `3.10.12`
- added 2G swap
- created project directory structure under `/home/projects/mango-talk`

---

### Current Directory Structure

```text
/home/projects/mango-talk
├── backend
├── frontend
├── uploads
├── logs
├── backups
└── scripts
```

# Mango Talk Backend — Version 0.1 Summary

---

## 🔐 Security / Configuration Decisions

- MySQL bind address set to `127.0.0.1`
- Backend secrets stored only in local `.env`
- `.env` **must never be committed**
- JWT authentication selected
- Password hashing enabled
- Project uses **local MySQL** instead of external DB service

---

## 🚀 Backend Progress Completed

### 1. FastAPI Project Initialized

**Completed:**

- Base app structure created
- `app/main.py`
- `app/core`
- `app/db`
- `app/models`
- `app/schemas`
- `app/api`
- `app/services`

---

### 2. Environment Variables Created

**Configured:**

- App name
- App environment
- App host / port
- MySQL connection info
- JWT secret
- Token expiration

---

### 3. Database Connection Established

**Completed:**

- Database `mango_talk` created
- Database user `mango_user@127.0.0.1` created
- SQLAlchemy engine configured
- DB health check endpoint works

---

### 4. Health Endpoints Completed

**Available endpoints:**

- `GET /`
- `GET /health`
- `GET /health/db`

---

### 5. User System Foundation Completed

**Implemented:**

- `users` table
- User model
- Registration schema
- Login schema
- Public user schema

---

### 6. Authentication Completed

**Implemented:**

- Password hashing
- Password verification
- JWT token creation
- Register endpoint
- Login endpoint
- Protected current-user endpoint

**Available auth endpoints:**

- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`

---

## ✅ Verified Functional Results

### Registration

**Confirmed working:**

- User registration succeeded
- First user created successfully

---

### Login

**Confirmed working:**

- Login with username works
- JWT access token returned successfully

---

### Protected Route

**Confirmed working:**

- `/users/me` rejects unauthenticated request
- `/users/me` returns current user info with valid token

---

## 🛠️ Problems Encountered and Fixes

### Problem 1: bcrypt / passlib Compatibility Error

**Symptom:**

- Registration failed with misleading error:
    ```
    ValueError: password cannot be longer than 72 bytes
    ```


**Actual cause:**

- Compatibility issue between `passlib` and newer `bcrypt`

**Fix:**

- Downgraded `bcrypt` to `4.3.0`

**Result:**

- Registration and login work normally

---

### Problem 2: MySQL Official APT Repo Signature Expired

**Symptom:**

- `apt update` reported MySQL repository GPG signature issue

**Current status:**

- Does not block current development
- Should be fixed later when package maintenance is needed

---

## 📌 Important Notes for Future Development

- Current Node version on server is not ideal LTS → upgrade before frontend initialization
- MySQL port `3306` restricted to localhost
- MySQL `33060` still listening → not urgent yet

---

### 🌐 Current Nginx Configuration

Currently serving:

- `chenglan.tech`
- `www.chenglan.tech`

---

### 🌍 Future Chat Deployment Plan

Use a dedicated subdomain:

- `talk.chenglan.tech`
- or `mango-talk.chenglan.tech`

---

## 📈 Recommended Next Steps

- Push project to GitHub
- Stabilize repository structure

### Backend

- Design chat core data model:
- `rooms`
- `room_members`
- `messages`
- Implement authenticated chat-related APIs
- Add WebSocket-based real-time messaging

### Frontend

- Initialize Vue frontend
- Connect frontend with authentication flow

### Deployment

- Configure Nginx subdomain for Mango Talk

---

## 🧠 Current Version Summary

**Version 0.1 means:**

- Environment is ready
- Backend authentication foundation is ready
- Project is now ready to enter:
- Chat-domain modeling
- Real-time communication stage