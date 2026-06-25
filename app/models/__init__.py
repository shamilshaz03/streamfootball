"""
Import every model so that `Base.metadata` is fully populated for
`Base.metadata.create_all(...)` and for Alembic's autogenerate.
"""
from app.models.admin import AdminUser  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.highlight import BroadcastMessage, Highlight  # noqa: F401
from app.models.match import Match  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.setting import SystemSetting  # noqa: F401
from app.models.standing import Standing  # noqa: F401
from app.models.stream import Stream  # noqa: F401
from app.models.team import Team  # noqa: F401
from app.models.tournament import Group, Tournament  # noqa: F401
from app.models.user import User  # noqa: F401
