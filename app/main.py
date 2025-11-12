"""
主应用入口
FastAPI 应用初始化和配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.controllers import tts_router
from app.utils import app_logger, ensure_output_dir, ensure_cache_dir


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    # 创建应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="基于 Edge TTS 的文本转语音 API 服务",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置 CORS
    # 生产环境使用配置的域名列表，开发环境允许所有来源
    cors_origins = settings.cors_origins if not settings.debug else ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(tts_router, prefix=settings.api_prefix)
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """全局异常处理器"""
        app_logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None
            }
        )
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时的初始化操作"""
        app_logger.info(f"{settings.app_name} v{settings.app_version} 启动中...")
        
        # 确保输出目录存在
        ensure_output_dir()
        app_logger.info(f"输出目录已准备: {settings.output_dir}")
        
        # 确保缓存目录存在
        if settings.enable_cache:
            ensure_cache_dir()
            app_logger.info(f"缓存目录已准备: {settings.cache_dir}")
        
        app_logger.info("应用启动完成")
    
    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时的清理操作"""
        app_logger.info("应用正在关闭...")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version
        }
    
    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": f"欢迎使用 {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs"
        }
    
    return app


# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

