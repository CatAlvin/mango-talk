# Mango Talk 开发日志

---

## Version 0.1 — 2026-04-02

### 项目阶段
后端基础能力已完成。  
项目已经从环境搭建阶段，进入到初步业务能力建设阶段。

### 已确认的项目定位
Mango Talk 是一个标准的聊天类 Web 应用，面向：

- 小团队沟通
- 朋友交流
- 校园 / 学生组织沟通

该项目的目标是做到：

- 具备实际可用性
- 可部署在 Ubuntu 服务器上
- 后续具备较好的界面展示效果
- 未来便于继续扩展迭代

### 已确认的技术栈

#### 前端
- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- SCSS
- Element Plus（部分使用）

#### 后端
- Python 3.10
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- python-dotenv
- passlib
- bcrypt
- python-jose
- WebSocket（计划中）

#### 基础设施
- Ubuntu 22.04
- Nginx
- MySQL 8
- systemd
- GitHub

---

## 服务器环境说明

### 已确认环境
- Ubuntu 22.04.5 LTS
- 2 vCPU
- 3.5 GiB 内存
- 40 GB 磁盘
- Nginx 已运行
- MySQL 已运行

### 已完成的重要环境调整
- 退出 Conda base 环境干扰
- 切换为系统 Python：`/usr/bin/python3`
- 确认 Python 版本为：`3.10.12`
- 增加 `2G swap`
- 在 `/home/projects/mango-talk` 下创建项目目录结构

---

## 当前目录结构

```text
/home/projects/mango-talk
├── backend
├── frontend
├── uploads
├── logs
├── backups
└── scripts
```

### 一、安全 / 配置决策

当前已确定以下基础安全与配置方案：

- MySQL 监听地址设置为 `127.0.0.1`
- 后端密钥仅保存在本地 `.env`
- `.env` 绝对不能提交到 GitHub
- 认证方案选择 JWT
- 已启用密码哈希
- 项目使用本地 MySQL，而非外部数据库服务

---

### 二、后端已完成进展

#### 1. FastAPI 项目初始化完成

**已完成：**
- 创建基础应用结构
- `app/main.py`
- `app/core`
- `app/db`
- `app/models`
- `app/schemas`
- `app/api`
- `app/services`

#### 2. 环境变量配置完成

**已配置：**
- 应用名称
- 应用环境
- 应用 host / port
- MySQL 连接信息
- JWT 密钥
- Token 过期时间

#### 3. 数据库连接建立完成

**已完成：**
- 创建数据库 `mango_talk`
- 创建数据库用户 `mango_user@127.0.0.1`
- 配置 SQLAlchemy engine
- 数据库健康检查接口可正常工作

#### 4. 健康检查接口完成

**当前可用接口：**
- `GET /`
- `GET /health`
- `GET /health/db`

#### 5. 用户系统基础完成

**已实现：**
- `users` 表
- `User` 模型
- 注册 schema
- 登录 schema
- 公共用户信息 schema

#### 6. 认证系统完成

**已实现：**
- 密码哈希
- 密码校验
- JWT token 生成
- 注册接口
- 登录接口
- 受保护的当前用户接口

**当前认证相关接口：**
- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`

---

### 三、已验证功能结果

#### 用户注册
**已确认正常：**
- 用户注册成功
- 第一个用户已成功创建

#### 用户登录
**已确认正常：**
- 可以使用用户名登录
- 成功返回 JWT access token

#### 受保护接口
**已确认正常：**
- `/users/me` 会拒绝未认证请求
- `/users/me` 在携带有效 token 时可正确返回当前用户信息

---

### 四、遇到的问题与修复

#### 问题 1：bcrypt / passlib 兼容性错误

**现象：**  
注册时出现误导性报错：
```text
ValueError: password cannot be longer than 72 bytes
```


**实际原因：**  
`passlib` 与较新版本 `bcrypt` 之间存在兼容性问题。

**修复方式：**  
将 `bcrypt` 降级到 `4.3.0`。

**结果：**  
注册与登录恢复正常。

---

#### 问题 2：MySQL 官方 APT 仓库签名过期

**现象：**  
执行 `apt update` 时出现 MySQL 仓库 GPG 签名错误。

**当前状态：**
- 不影响当前开发
- 后续若需要维护系统包，应再修复该问题

---

### 五、后续开发的重要备注

- 服务器当前 Node 版本不是理想的 LTS 版本，建议在初始化前端前升级
- MySQL 的 `3306` 端口已限制为仅本机访问
- MySQL 的 `33060` 端口仍在监听，但目前不紧急处理

---

### 六、当前 Nginx 配置

当前正在服务的域名：

- `chenglan.tech`
- `www.chenglan.tech`

---

### 七、后续聊天系统部署规划

建议使用独立子域名：

- `talk.chenglan.tech`
- 或 `mango-talk.chenglan.tech`

---

### 八、建议的下一步工作

#### 仓库层面
- 将项目推送到 GitHub
- 稳定当前仓库结构

#### 后端层面
- 设计聊天核心数据模型：
- `rooms`
- `room_members`
- `messages`
- 实现需要登录后才能访问的聊天相关 API
- 增加基于 WebSocket 的实时消息能力

#### 前端层面
- 初始化 Vue 前端项目
- 将前端接入登录认证流程

#### 部署层面
- 为 Mango Talk 配置独立的 Nginx 子域名反向代理

---

### 九、当前版本总结

**Version 0.1 表示：**

- 开发环境已经准备完成
- 后端认证基础已经建立完成
- 项目已经可以正式进入以下阶段：
- 聊天领域建模
- 实时通信能力建设

---

## Version 0.2 — 2026-04-03

### 当前阶段
后端认证系统与聊天室核心 REST 接口已完成，项目已从“环境搭建阶段”进入“聊天室核心业务可用阶段”。

当前系统已经不是只有骨架，而是已经具备：
- 用户注册
- 用户登录
- JWT 鉴权
- 当前用户识别
- 私聊房间创建
- 群聊房间创建
- 我的房间列表
- 发送消息
- 查看房间历史消息
- 回复消息
- 撤回消息

---

### 当前版本定位
Version 0.2 的意义是：

> Mango Talk 后端已经具备“基础可聊天能力”，目前差的主要是：
> - WebSocket 实时推送
> - 前端 Vue 页面
> - 文件上传
> - 更完整的管理能力

也就是说，现在系统已经能完成“静态版聊天室”的核心业务流程，只是还没有进入“实时通信”和“前端交互”阶段。

---

### 已确认的技术路线

#### 前端（计划中）
- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- SCSS
- Element Plus（部分辅助使用）

#### 后端（当前已在使用）
- Python 3.10
- FastAPI
- Uvicorn
- SQLAlchemy
- PyMySQL
- python-dotenv
- passlib
- bcrypt
- python-jose
- WebSocket（下一阶段实现）

#### 基础设施
- Ubuntu 22.04
- Nginx
- MySQL 8
- systemd
- GitHub

---

### 当前目录结构
```text
/home/projects/mango-talk
├── backend
├── frontend
├── uploads
├── logs
├── backups
├── scripts
└── docs
```

## 1. 环境与基础配置

### 已完成
- 退出 Conda base 环境干扰
- 改用系统 Python `/usr/bin/python3`
- 确认 Python 版本为 `3.10.12`
- 增加 `2G swap`
- 创建项目目录结构
- 创建后端虚拟环境 `.venv`
- 安装后端基础依赖
- 创建 `.env` 本地配置文件

### 已确认
- Nginx 运行正常
- MySQL 运行正常
- 项目目录独立于现有博客项目
- 博客站点当前使用 `chenglan.tech` 与 `www.chenglan.tech`

---

## 2. 数据库与安全基础

### 已完成
- MySQL 监听地址收紧为 `127.0.0.1`
- 创建数据库 `mango_talk`
- 创建数据库用户 `mango_user@127.0.0.1`
- 数据库连接字符串接入 FastAPI
- `/health/db` 数据库健康检查成功

### 安全决策
- `.env` 不提交 GitHub
- 使用 JWT 做登录认证
- 使用密码哈希，不保存明文密码
- 当前数据库仅供本机后端访问

---

## 3. 用户系统

### 已完成
- `users` 表
- 用户模型 `User`
- 注册 schema
- 登录 schema
- 用户公开信息 schema
- 注册接口
- 登录接口
- `/users/me` 当前用户接口

### 当前可用接口
- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`

### 已验证
- 用户注册成功
- 用户登录成功
- JWT token 返回成功
- 未带 token 访问 `/users/me` 会被拒绝
- 带有效 token 访问 `/users/me` 能正确返回当前用户信息

---

## 4. 聊天室核心数据模型

已完成以下三张核心表：

### `chat_rooms`
**作用：**
- 表示一个聊天房间
- 同时支持单聊与群聊

**关键字段：**
- `type`
- `name`
- `owner_id`
- `avatar_url`
- `description`
- `is_active`
- `created_at`
- `updated_at`

### `chat_room_members`
**作用：**
- 表示某用户是否属于某房间
- 用于成员关系、权限、禁言

**关键字段：**
- `room_id`
- `user_id`
- `role`
- `nickname_in_room`
- `is_muted`
- `joined_at`

**已确认：**
- 存在联合唯一约束 `uq_room_user`
- 保证同一用户不能重复加入同一房间

### `messages`
**作用：**
- 表示房间中的消息记录

**关键字段：**
- `room_id`
- `sender_id`
- `message_type`
- `content`
- `reply_to_message_id`
- `is_recalled`
- `recalled_at`
- `created_at`
- `updated_at`

**已确认：**
- `reply_to_message_id` 外键已建立
- 支持“回复消息”的数据层能力
- 支持“撤回消息”的软删除式记录能力

---

## 5. 房间系统

### 已完成
- 创建私聊房间接口
- 创建群聊房间接口
- 获取我的房间列表接口

### 当前可用接口
- `POST /rooms/private`
- `POST /rooms/group`
- `GET /rooms/mine`

### 已验证能力
- 可以为当前用户创建私聊
- 私聊重复创建时不会生成新房间，而是返回已有房间
- 可以创建群聊并添加成员
- 可以正确返回当前用户参与的房间列表

### 当前已验证房间示例
- 群聊：`芒果测试`
- 私聊：`与 alice 的私聊房间`

### 设计说明
- 单聊与群聊统一抽象为 `room`
- 私聊通过 `display_name` 显示对方用户名
- 群聊通过 `name` 直接作为显示名称

---

## 6. 消息系统（REST 版）

### 已完成
- 发送消息接口
- 获取房间历史消息接口
- 撤回消息接口
- 回复消息能力（通过 `reply_to_message_id` 实现）

### 当前可用接口
- `POST /messages`
- `GET /messages/room/{room_id}`
- `POST /messages/{message_id}/recall`

### 已验证结果

#### 发送消息
已成功向私聊房间发送第一条文本消息：

- 内容：`你好，Alice！这是我的第一条私聊消息`

#### 回复消息
已成功发送回复消息：

- 内容：`这是对第一条消息的回复`
- `reply_to_message_id = 1`

#### 获取历史消息
已成功获取私聊房间历史消息列表：

- 返回消息顺序正确
- 返回字段符合预期
- 回复消息链路正常

#### 撤回消息
已成功撤回消息 `id=2`：

- `is_recalled = true`
- `recalled_at` 已记录
- 再次查询消息历史时撤回状态仍保留

---

## 7. 当前已验证的整体业务链路

目前后端已经完成并验证通过以下完整链路：

1. 注册用户
2. 登录用户
3. 获取 JWT token
4. 校验当前登录用户
5. 创建私聊房间
6. 创建群聊房间
7. 获取我的房间列表
8. 在房间中发送文本消息
9. 回复已有消息
10. 拉取房间历史消息
11. 撤回自己发送的消息

这说明 Mango Talk 后端当前已经具备：

- 用户身份能力
- 聊天容器能力
- 基础消息流转能力

---

## 8. 当前遇到的问题与处理记录

### 问题 1：bcrypt / passlib 兼容问题

**现象：**
- 注册时抛出误导性错误：  
`ValueError: password cannot be longer than 72 bytes`

**实际原因：**
- `passlib` 与较新版本 `bcrypt` 兼容性问题

**处理：**
- 将 `bcrypt` 降级到 `4.3.0`

**结果：**
- 注册与登录恢复正常

### 问题 2：MySQL 官方 apt 仓库签名过期

**现象：**
- `apt update` 出现 MySQL 仓库 GPG signature error

**当前状态：**
- 不影响当前开发
- 后续如需维护系统包时应修复

---

## 9. 当前值得记录的工程判断

### 1）当前数据库设计是正确方向
现在的 `users` + `chat_rooms` + `chat_room_members` + `messages` 四张核心表，已经足够支撑下一阶段：

- WebSocket 房间广播
- 前端房间列表
- 前端聊天窗口
- 撤回 / 回复展示逻辑

**结论：**
- 不需要返工

### 2）当前消息系统仍是 REST 版本
现在消息接口已可用，但尚未实时化。  
目前状态更接近：

- “静态聊天室”
- “手动请求式消息系统”

下一阶段会通过 WebSocket 把它升级成真正的实时聊天。

### 3）前端尚未开始初始化
目前所有进展都集中在后端。  
Vue 3 + Vite 前端项目还没有正式初始化，后续应在 WebSocket 或消息接口进一步稳定后开始。

### 4）当前 Node 版本仍不是理想 LTS
服务器上的 Node 当前可用，但不是最佳长期版本。  
在正式初始化前端前，建议升级到更合适的 LTS 版本。

---

## 10. 当前系统边界

### Version 0.2 已支持
- 用户认证
- 房间管理
- 基础消息流

### Version 0.2 尚未支持
- WebSocket 实时聊天
- 文件上传
- 图片消息
- 在线状态
- 输入中状态
- 已读未读
- 群管理细化
- 敏感词 / 审计日志
- Vue 前端页面
- Nginx 子域名反代到 Mango Talk
- HTTPS 正式接入

---

## 11. 下一步建议

建议下一阶段进入：

## Version 0.3 目标
**WebSocket 实时消息能力**

### 建议任务
- 设计 WebSocket 连接方式
- 实现按 room 建立连接
- 实现房间广播
- 实现消息发送后实时推送
- 验证多用户实时收发效果

### 预期结果
完成后，项目会从“能发消息”升级成“能实时聊天”。

---

## 12. 当前版本总结

**Version 0.2 表示：**

Mango Talk 后端认证、房间、消息三大核心模块已经建立完成，系统已具备基础聊天业务能力，下一阶段将进入实时通信能力建设。