# 生产环境部署指南

## 部署信息

- **域名**: ttsedge.egg404.com
- **端口**: 5005
- **协议**: HTTPS

## 部署步骤

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# 安装 Nginx（用于反向代理）
sudo apt install nginx -y
```

### 2. 项目部署

```bash
# 克隆或上传项目到服务器
cd /opt
git clone <your-repo-url> edge-tts
cd edge-tts

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.production .env
```

或手动创建 `.env`：

```env
APP_NAME=Edge TTS API
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=5005
DOMAIN=ttsedge.egg404.com
BASE_URL=https://ttsedge.egg404.com
API_PREFIX=/api/v1
OUTPUT_DIR=./output
CACHE_DIR=./cache
MAX_FILE_SIZE_MB=50
ENABLE_CACHE=true
DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
DEFAULT_RATE=+0%
DEFAULT_VOLUME=+0%
DEFAULT_PITCH=+0Hz
RUSSIAN_SENTENCE_RATE=-30%
RUSSIAN_LONG_SENTENCE_THRESHOLD=50
MAX_TEXT_LENGTH=5005
```

### 4. 创建系统服务

创建 systemd 服务文件 `/etc/systemd/system/edge-tts.service`：

```ini
[Unit]
Description=Edge TTS API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/edge-tts
Environment="PATH=/opt/edge-tts/venv/bin"
ExecStart=/opt/edge-tts/venv/bin/python3 /opt/edge-tts/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable edge-tts
sudo systemctl start edge-tts
sudo systemctl status edge-tts
```

### 5. 配置 Nginx 反向代理

创建 Nginx 配置文件 `/etc/nginx/sites-available/ttsedge.egg404.com`：

```nginx
server {
    listen 80;
    server_name ttsedge.egg404.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ttsedge.egg404.com;

    # SSL 证书配置（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/ttsedge.egg404.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ttsedge.egg404.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 客户端最大上传大小
    client_max_body_size 10M;

    # 日志
    access_log /var/log/nginx/ttsedge-access.log;
    error_log /var/log/nginx/ttsedge-error.log;

    # 反向代理到应用
    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件缓存（音频文件）
    location ~* \.(mp3|wav|webm)$ {
        proxy_pass http://127.0.0.1:5005;
        proxy_cache_valid 200 1h;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        add_header Cache-Control "public, max-age=3600";
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/ttsedge.egg404.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 配置 SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d ttsedge.egg404.com

# 自动续期
sudo certbot renew --dry-run
```

### 7. 防火墙配置

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 确保本地端口 5005 不被外部访问（仅通过 Nginx）
sudo ufw status
```

## 验证部署

### 1. 检查服务状态

```bash
# 检查应用服务
sudo systemctl status edge-tts

# 检查 Nginx
sudo systemctl status nginx

# 查看应用日志
tail -f /opt/edge-tts/logs/app_*.log
```

### 2. 测试 API

```bash
# 健康检查
curl https://ttsedge.egg404.com/health

# 测试 TTS
curl -X POST "https://ttsedge.egg404.com/api/v1/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "测试",
    "voice": "zh-CN-XiaoxiaoNeural"
  }'
```

### 3. 访问 API 文档

- Swagger UI: https://ttsedge.egg404.com/docs
- ReDoc: https://ttsedge.egg404.com/redoc

## 维护命令

```bash
# 重启服务
sudo systemctl restart edge-tts

# 查看日志
sudo journalctl -u edge-tts -f
tail -f /opt/edge-tts/logs/app_*.log

# 重新加载 Nginx
sudo nginx -t && sudo systemctl reload nginx

# 清理缓存（如果需要）
rm -rf /opt/edge-tts/cache/*
rm -rf /opt/edge-tts/output/*
```

## 监控建议

1. **日志监控**: 定期检查应用日志和 Nginx 日志
2. **磁盘空间**: 监控缓存目录和输出目录的磁盘使用
3. **服务健康**: 设置健康检查监控
4. **性能监控**: 监控 API 响应时间和错误率

## 备份建议

定期备份：
- 配置文件（`.env`）
- 缓存目录（可选，可重新生成）
- 日志文件

## 故障排查

### 服务无法启动

```bash
# 检查端口是否被占用
sudo lsof -i :5005

# 检查 Python 环境
source venv/bin/activate
python3 --version
pip list
```

### Nginx 502 错误

```bash
# 检查应用是否运行
sudo systemctl status edge-tts

# 检查端口
curl http://127.0.0.1:5005/health
```

### SSL 证书问题

```bash
# 检查证书
sudo certbot certificates

# 更新证书
sudo certbot renew
```

## 性能优化

1. **启用缓存**: 确保 `ENABLE_CACHE=true`
2. **Nginx 缓存**: 已配置静态文件缓存
3. **Gunicorn**: 如需更高性能，可使用 Gunicorn + Uvicorn workers

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:5005
```

