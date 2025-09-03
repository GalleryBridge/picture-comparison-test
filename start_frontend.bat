@echo off
echo 启动PDF图纸尺寸分析系统 - 前端服务
echo =====================================

cd frontend

echo 检查Node.js依赖...
if not exist "node_modules" (
    echo 安装前端依赖...
    npm install
)

echo 启动前端开发服务器...
npm run dev

pause
