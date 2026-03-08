from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from ..constants import AccountStatus, UserRole
from ..helpers.utils import error_response
from ..models import Company, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return error_response("Missing email or password")

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return error_response("Invalid credentials", 401)

    if user.account_status == AccountStatus.BLACKLISTED:
        return error_response("Account is blacklisted", 403)

    additional_claims = {"role": user.role, "id": user.id}

    user_info = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }

    if user.role == UserRole.COMPANY:
        company = Company.query.filter_by(user_id=user.id).first()
        if company:
            additional_claims["approval_status"] = company.approval_status
            user_info["approval_status"] = company.approval_status

    access_token = create_access_token(
        identity=user.email, additional_claims=additional_claims
    )
    return (
        {
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "user": user_info,
            },
        },
        200,
    )
