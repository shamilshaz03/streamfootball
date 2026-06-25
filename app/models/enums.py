"""
Shared Python enums mapped to Postgres enum / varchar columns.
"""
import enum


class MatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    HALFTIME = "halftime"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class StreamType(str, enum.Enum):
    HLS = "hls"
    MP4 = "mp4"
    EXTERNAL = "external"
    WEBAPP = "webapp"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    MODERATOR = "moderator"


class TournamentType(str, enum.Enum):
    LEAGUE = "league"
    KNOCKOUT = "knockout"
    GROUP_KNOCKOUT = "group_knockout"


class BroadcastType(str, enum.Enum):
    REMINDER_1H = "reminder_1h"
    REMINDER_30M = "reminder_30m"
    REMINDER_15M = "reminder_15m"
    MATCH_STARTED = "match_started"
    HALF_TIME = "half_time"
    MATCH_FINISHED = "match_finished"
