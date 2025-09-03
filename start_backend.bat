@echo off
echo 启动PDF图纸尺寸分析系统 - 后端服务
echo =====================================

cd backend

echo 检查Python虚拟环境...
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate

echo 安装依赖包...
pip install -r requirements.txt

echo 复制环境配置文件...
if not exist ".env" (
    copy .env.example .env
    echo 请编辑 backend\.env 文件配置数据库等信息
)

echo 启动FastAPI服务器...
python main.py

pause
