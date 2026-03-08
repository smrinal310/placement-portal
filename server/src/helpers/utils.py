import mimetypes
import os
from datetime import UTC, datetime

from flask import Flask, jsonify
from werkzeug.datastructures import FileStorage

from ..constants import AccountStatus, UserRole
from ..models import User, db


def success_response(
    message: str,
    data: dict | list | None = None,
    status_code: int = 200,
):
    body: dict = {"message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error_response(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


MIME_MAP: dict[str, set[str]] = {
    "pdf": {"application/pdf"},
    "docx": {
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
    },
    "png": {"image/png"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
}


def validate_file(
    file: FileStorage,
    allowed_extensions: set[str],
    allowed_mimetypes: set[str],
) -> tuple[bool, str]:
    """Validate both extension and MIME type of an upload.

    Returns (True, "") on success, (False, "reason") on failure.
    """
    if not file or not file.filename:
        return False, "No file provided"

    ext = (
        file.filename.rsplit(".", 1)[-1].lower()
        if "." in file.filename
        else ""
    )
    if ext not in allowed_extensions:
        return False, f"Invalid file extension '.{ext}'"

    mime, _ = mimetypes.guess_type(file.filename)
    if mime not in allowed_mimetypes:
        return False, f"Invalid MIME type '{mime}'"

    return True, ""


def escape_like(value: str) -> str:
    """Escape special SQL LIKE characters (%, _) in user input."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def parse_iso_datetime(iso_str: str | None) -> datetime | None:
    if not iso_str:
        return None
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        return dt.astimezone(UTC).replace(tzinfo=None)
    return dt


def create_admin(app: Flask) -> None:
    """Ensure exactly one admin account exists (created programmatically)."""
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
