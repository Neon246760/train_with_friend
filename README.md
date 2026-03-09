# Train With Friend

一个简单的训练记录网站，方便你和朋友互相促进。

## 功能

*   **用户登录**：管理员添加账号，无公开注册。
*   **好友系统**：添加好友，查看好友训练记录。
*   **训练记录**：
    *   **慢跑**：记录距离、配速、心率。
    *   **间歇跑**：记录多组训练（距离 x 组数）。
    *   **素质训练**：文本记录。
*   **历史查询**：按日期筛选，支持查看好友记录。

## 部署说明

### 使用 Docker 部署 (推荐)

1.  确保已安装 Docker 和 Docker Compose。
2.  在项目根目录下运行：

    ```bash
    docker-compose up -d --build
    ```

3.  访问 `http://localhost:8000` (或服务器 IP:8000)。

### 添加用户

由于没有注册页面，管理员需要通过脚本添加用户。

1.  **在 Docker 容器中添加**：

    ```bash
    # 进入后端容器
    docker exec -it train-backend bash
    
    # 运行创建用户脚本
    python create_user.py <username> <password>
    # 例如：python create_user.py admin 123456
    ```

2.  **本地开发时添加**：

    ```bash
    cd backend
    pip install -r requirements.txt
    python create_user.py <username> <password>
    ```

## 开发说明

### 后端 (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
后端运行在 `http://localhost:8000`。

### 前端 (Vue 3 + Vite)

```bash
cd frontend
npm install
npm run dev
```
前端运行在 `http://localhost:5173`。

注意：前端开发模式下，请确保 `vite.config.js` 中的代理配置正确指向后端地址。
