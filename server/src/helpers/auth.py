from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from ..constants import UserRole
from ..helpers.utils import error_response
from ..models import Company, Student, User


def roles_required(*allowed_roles: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                return error_response("Access required", 403)
            return fn(*args, **kwargs)

        return decorator

    return wrapper


admin_required = roles_required(UserRole.ADMIN)
company_required = roles_required(UserRole.COMPANY)
student_required = roles_required(UserRole.STUDENT)


def get_current_company() -> tuple[User, Company | None]:
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    company = Company.query.filter_by(user_id=user.id).first()
    return user, company


def get_current_student() -> tuple[User, Student | None]:
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    student = Student.query.filter_by(user_id=user.id).first()
    return user, student
