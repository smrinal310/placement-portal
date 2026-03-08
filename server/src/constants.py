from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    COMPANY = "company"
    STUDENT = "student"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DriveStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ApplicationStatus(StrEnum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    SELECTED = "selected"
    REJECTED = "rejected"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


class LogoLimits:
    ALLOWED_LOGO_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}
    ALLOWED_LOGO_MIMETYPES: set[str] = {"image/png", "image/jpeg"}
    MAX_LOGO_SIZE: int = 2 * 1024 * 1024


class ResumeLimits:
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx"}
    ALLOWED_MIMETYPES: set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
    }
    MAX_SIZE: int = 5 * 1024 * 1024


class ExportJobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
