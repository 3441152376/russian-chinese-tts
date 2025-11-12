# 快速修复指南

## 问题：ModuleNotFoundError: No module named 'pydantic_settings'

### 立即解决方案

在服务器上执行以下命令：

```bash
# 1. 进入项目目录
cd /www/wwwroot/edfe

# 2. 激活虚拟环境（如果使用）
source venv/bin/activate

# 3. 安装缺失的包
pip install pydantic-settings==2.5.2

# 4. 或者重新安装所有依赖
pip install -r requirements.txt

# 5. 验证安装
python3 -c "import pydantic_settings; print('安装成功')"

# 6. 重新启动服务
python3 run.py
```

### 如果使用 systemd 服务

```bash
# 确保虚拟环境路径正确
# 编辑服务文件
sudo nano /etc/systemd/system/edge-tts.service

# 确保 ExecStart 路径正确：
# ExecStart=/www/wwwroot/edfe/venv/bin/python3 /www/wwwroot/edfe/run.py

# 重新加载并重启
sudo systemctl daemon-reload
sudo systemctl restart edge-tts
sudo systemctl status edge-tts
```

### 检查依赖是否完整

```bash
# 检查已安装的包
pip list | grep -E "(pydantic|fastapi|uvicorn|edge-tts)"

# 应该看到：
# fastapi           0.115.0
# pydantic          2.9.2
# pydantic-settings 2.5.2
# uvicorn           0.32.0
# edge-tts          7.2.3
```

### 如果仍然失败

1. **检查 Python 版本**（需要 >= 3.9）：
   ```bash
   python3 --version
   ```

2. **使用国内镜像源**（如果下载慢）：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **检查虚拟环境**：
   ```bash
   which python3
   # 应该指向虚拟环境中的 python3
   ```

