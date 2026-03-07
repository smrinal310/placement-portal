class UserRole:
    ADMIN = "admin"
    COMPANY = "company"
    STUDENT = "student"


class ApprovalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DriveStatus:
    PENDING = "pending"
    APPROVED = "approved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ApplicationStatus:
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    SELECTED = "selected"
    REJECTED = "rejected"


class AccountStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


class LogoLimits:
    ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_LOGO_SIZE = 2 * 1024 * 1024
