from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from ..constants import ApprovalStatus, UserRole
from ..models import Company, User


def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != required_role:
                return jsonify(
                    {
                        "message": f"{required_role.capitalize()} "
                        "access required"
                    }
                ), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def approved_company_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != UserRole.COMPANY:
                return jsonify({"message": "Company access required"}), 403
            if claims.get("approval_status") != ApprovalStatus.APPROVED:
                return jsonify(
                    {
                        "message": "Company account is "
                        "pending approval or rejected"
                    }
                ), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


admin_required = role_required(UserRole.ADMIN)
company_required = role_required(UserRole.COMPANY)
student_required = role_required(UserRole.STUDENT)


def get_current_company():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    company = Company.query.filter_by(user_id=user.id).first()
    return user, company
