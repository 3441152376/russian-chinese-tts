# 安装和部署说明

## 问题排查

如果遇到 `ModuleNotFoundError: No module named 'pydantic_settings'` 错误，请按照以下步骤解决：

## 解决方案

### 1. 安装依赖

在服务器上执行以下命令：

```bash
# 进入项目目录
cd /www/wwwroot/edfe

# 激活虚拟环境（如果使用虚拟环境）
source venv/bin/activate  # 或你的虚拟环境路径

# 安装所有依赖
pip install -r requirements.txt

# 或者单独安装缺失的包
pip install pydantic-settings==2.5.2
```

### 2. 检查 Python 版本

确保 Python 版本 >= 3.9：

```bash
python3 --version
```

### 3. 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 4. 验证安装

```bash
python3 -c "import pydantic_settings; print('pydantic-settings 安装成功')"
```

### 5. 重新启动服务

```bash
# 如果使用 systemd
sudo systemctl restart edge-tts

# 或者直接运行
python3 run.py
```

## 完整安装步骤

```bash
# 1. 进入项目目录
cd /www/wwwroot/edfe

# 2. 创建虚拟环境（如果还没有）
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装所有依赖
pip install -r requirements.txt

# 6. 验证安装
python3 -c "from app.config import settings; print('配置加载成功')"

# 7. 测试运行
python3 run.py
```

## 常见问题

### Q: 权限错误

如果遇到权限错误，可能需要使用 sudo 或修改文件权限：

```bash
# 修改项目目录权限
sudo chown -R $USER:$USER /www/wwwroot/edfe
```

### Q: pip 安装慢

使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 虚拟环境路径问题

确保 systemd 服务文件中的路径正确：

```ini
[Service]
Environment="PATH=/www/wwwroot/edfe/venv/bin"
ExecStart=/www/wwwroot/edfe/venv/bin/python3 /www/wwwroot/edfe/run.py
```

## 依赖列表

主要依赖包：
- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- edge-tts==7.2.3
- pydantic==2.9.2
- pydantic-settings==2.5.2
- python-multipart==0.0.12
- loguru==0.7.2

