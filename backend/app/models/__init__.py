"""汇总 ORM 模型，确保模型被导入并注册到 Base.metadata。"""

from app.models import user  # noqa
from app.models import chat_message  # noqa: E402,F401
from app.models import chat_session  # noqa: E402,F401
from app.models import favorite  # noqa: E402,F401
from app.models import heritage_site  # noqa: E402,F401
from app.models import itinerary  # noqa: E402,F401
