import os
from datetime import UTC, datetime

from ..constants import AccountStatus, LogoLimits, UserRole
from ..models import User, db


def create_admin(app):
    """
    Ensure exactly one admin account exists (created programmatically).
    """

    admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@1234")

    existing = User.query.filter_by(role=UserRole.ADMIN).first()
    if existing:
        return

    admin = User(
        email=admin_email,
        role=UserRole.ADMIN,
        account_status=AccountStatus.ACTIVE,
    )
    admin.set_password(admin_password)
    db.session.add(admin)
    db.session.commit()
    app.logger.info(f"Admin user created: {admin_email}")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in LogoLimits.ALLOWED_LOGO_EXTENSIONS
    )


def parse_iso_datetime(iso_str):
    if not iso_str:
        return None
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        return dt.astimezone(UTC).replace(tzinfo=None)
    return dt
