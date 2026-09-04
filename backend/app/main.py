"""创建并暴露 FastAPI 应用实例。"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, settings
from app.routers.health import router as health_router

logger = logging.getLogger(__name__)


def setup_logging(log_level: str) -> None:
    """按配置初始化应用日志。"""

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )
    logger.debug("日志级别已设置为: %s", log_level.upper())


def create_app(app_settings: Settings = settings) -> FastAPI:
    """创建一个配置驱动的 FastAPI 应用实例。"""

    setup_logging(app_settings.log_level)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "服务启动: service=%s version=%s env=%s",
            app_settings.project_name,
            app_settings.version,
            app_settings.app_env,
        )
        yield

    app = FastAPI(
        title=app_settings.project_name,
        version=app_settings.version,
        debug=app_settings.debug,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api")
    return app


app = create_app()
