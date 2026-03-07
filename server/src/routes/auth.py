from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from ..constants import AccountStatus, UserRole
from ..models import Company, Student, User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json()

    # Required fields check
    required_fields = ["email", "password", "full_name", "branch", "year"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    try:
        user = User(
            email=data["email"],
            role=UserRole.STUDENT,
            account_status=AccountStatus.ACTIVE,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()  # To get user.id

        student = Student(
            user_id=user.id,
            full_name=data["full_name"],
            branch=data["branch"],
            year=data["year"],
            cgpa=data.get("cgpa", 0.0),
            phone=data.get("phone"),
            gender=data.get("gender"),
        )
        db.session.add(student)
        db.session.commit()

        return jsonify(
            {"message": "Student registered successfully", "user_id": user.id}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json()

    required_fields = [
        "email",
        "password",
        "company_name",
        "hr_name",
        "hr_contact",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    try:
        user = User(
            email=data["email"],
            role=UserRole.COMPANY,
            account_status=AccountStatus.ACTIVE,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        company = Company(
            user_id=user.id,
            company_name=data["company_name"],
            hr_name=data["hr_name"],
            hr_contact=data["hr_contact"],
            website=data.get("website"),
            industry=data.get("industry"),
        )
        db.session.add(company)
        db.session.commit()

        return jsonify(
            {
                "message": "Company registered. Pending approval from admin.",
                "user_id": user.id,
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    if user.account_status != AccountStatus.BLACKLISTED:
        return jsonify({"message": "Account is blacklisted"}), 403

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
    return jsonify(
        {
            "access_token": access_token,
            "user": user_info,
        }
    ), 200
