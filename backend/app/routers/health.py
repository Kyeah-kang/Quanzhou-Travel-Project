"""提供服务存活检查接口。"""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(request: Request) -> dict[str, str]:
    """返回应用的基础运行状态。"""

    app_settings = request.app.state.settings
    return {
        "status": "ok",
        "service": app_settings.project_name,
        "version": app_settings.version,
    }
