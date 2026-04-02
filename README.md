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
- WebSocket (planned for real-time messaging)

### Database / Storage
- MySQL 8
- Local file storage on Ubuntu server

### Deployment
- Ubuntu 22.04
- Nginx
- systemd
- GitHub for version control

## Current Progress

### v0.2
Backend core chat capability has been completed.

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

Verified workflows:
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
- Mango Talk backend already supports **basic non-real-time chat flow**
- The project is ready to move into the **WebSocket real-time messaging stage**

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

## 本地在服务器上运行后端
```bash
cd /home/projects/mango-talk/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 开发路线图（Roadmap）

### v0.3 — 实时消息能力
- 实现 WebSocket 认证
- 实现基于房间的 WebSocket 连接
- 实现房间内实时广播
- 打通 REST 消息创建与 WebSocket 实时推送
- 验证多用户实时聊天链路

### v0.4 — 前端初始化
- 初始化 Vue 3 + Vite 前端项目
- 搭建登录页
- 搭建聊天主布局
- 搭建房间列表面板
- 搭建消息列表面板
- 打通前端认证流程与后端 JWT
- 对接前端房间接口与消息接口

### v0.5 — 上传能力与更丰富的聊天功能
- 图片上传
- 文件上传
- 增加消息附件模型
- 支持更丰富的消息渲染
- 支持房间头像 / 用户头像

### v0.6 — 部署与生产环境加固
- 配置 Mango Talk 独立子域名
- 使用 Nginx 为前后端配置反向代理
- 为后端配置 systemd 服务
- 使用 Certbot 配置 HTTPS
- 完成环境清理与生产配置优化
- 改进日志能力

---

## 备注（Notes）

- 密钥与敏感信息绝对不能提交到代码仓库
- `backend/.env` 仅保存在本地
- 前端初始化目前尚未开始
- 当前后端版本为 `v0.2`
- 现有博客站点 `chenglan.tech` 的部署应继续与 Mango Talk 保持隔离