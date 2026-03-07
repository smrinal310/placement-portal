import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    ApprovalStatus,
    DriveStatus,
    LogoLimits,
    UserRole,
)
from src.helpers.auth import company_required, get_current_company
from src.helpers.utils import allowed_file, parse_iso_datetime
from src.models import Application, Company, PlacementDrive, User, db

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


@company_bp.route("/register", methods=["POST"])
def register():
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
            description=data.get("description"),
        )
        db.session.add(company)
        db.session.commit()

        return jsonify(
            {"message": "Registration successful. Awaiting admin approval."}
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


@company_bp.route("/profile", methods=["GET"])
@company_required
def get_profile():
    _, company = get_current_company()
    if not company:
        return jsonify({"message": "Company profile not found"}), 404

    return jsonify(
        {
            "id": company.id,
            "company_name": company.company_name,
            "hr_name": company.hr_name,
            "hr_contact": company.hr_contact,
            "website": company.website,
            "industry": company.industry,
            "description": company.description,
            "address": company.address,
            "logo_filename": company.logo_filename,
            "approval_status": company.approval_status,
        }
    ), 200


@company_bp.route("/profile", methods=["PUT"])
@company_required
def update_profile():
    _, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return jsonify(
            {"message": "Your company is pending admin approval"}
        ), 403

    data = request.get_json()
    allowed_updates = [
        "hr_name",
        "hr_contact",
        "website",
        "industry",
        "description",
        "address",
    ]
    for field in allowed_updates:
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


@company_bp.route("/profile/logo", methods=["POST"])
@company_required
def upload_logo():
    _, company = get_current_company()

    if "logo" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["logo"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > LogoLimits.MAX_LOGO_SIZE:
            return jsonify(
                {"message": "File exceeds maximum size of 2MB"}
            ), 400

        filename = secure_filename(file.filename)
        new_filename = f"{company.id}_{filename}"
        upload_folder = os.path.join(
            current_app.root_path, "..", "static", "uploads", "logos"
        )
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, new_filename)
        file.save(file_path)

        company.logo_filename = new_filename
        db.session.commit()
        return jsonify({"message": "Logo uploaded successfully"}), 200

    return jsonify({"message": "Invalid file format"}), 400


@company_bp.route("/dashboard", methods=["GET"])
@company_required
def get_dashboard():
    _, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return jsonify(
            {
                "message": "Your company is pending admin approval",
                "approval_status": company.approval_status,
            }
        ), 200

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_data = []

    for d in drives:
        applicant_count = Application.query.filter_by(drive_id=d.id).count()
        shortlisted_count = Application.query.filter_by(
            drive_id=d.id, status=ApplicationStatus.SHORTLISTED
        ).count()
        selected_count = Application.query.filter_by(
            drive_id=d.id, status=ApplicationStatus.SELECTED
        ).count()

        drive_data.append(
            {
                "drive_id": d.id,
                "job_title": d.job_title,
                "status": d.status,
                "applicant_count": applicant_count,
                "shortlisted_count": shortlisted_count,
                "selected_count": selected_count,
                "deadline": d.application_deadline.isoformat()
                if d.application_deadline
                else None,
            }
        )

    return jsonify(
        {
            "approval_status": company.approval_status,
            "total_drives": len(drives),
            "drives": drive_data,
        }
    ), 200


@company_bp.route("/drives", methods=["POST"])
@company_required
def create_drive():
    user, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return jsonify({"message": "Company not approved"}), 403

    if user.account_status == AccountStatus.BLACKLISTED:
        return jsonify({"message": "Account blacklisted"}), 403

    data = request.get_json()

    try:
        app_deadline = parse_iso_datetime(data["application_deadline"])
        now = datetime.utcnow()

        if app_deadline < now:
            return jsonify(
                {"message": "application_deadline must be a future datetime"}
            ), 400
    except (KeyError, ValueError, TypeError):
        return jsonify(
            {"message": "application_deadline is missing or invalid format"}
        ), 400

    min_cgpa = float(data.get("min_cgpa", 0.0))
    if not (0.0 <= min_cgpa <= 10.0):
        return jsonify(
            {"message": "min_cgpa must follow between 0.0 and 10.0"}
        ), 400

    min_year = int(data.get("min_year", 1))
    max_year = int(data.get("max_year", 4))
    if min_year > max_year:
        return jsonify({"message": "min_year must be <= max_year"}), 400

    try:
        drive_date = parse_iso_datetime(data.get("drive_date"))

        drive = PlacementDrive(
            company_id=company.id,
            job_title=data["job_title"],
            job_description=data["job_description"],
            job_location=data.get("job_location"),
            job_type=data.get("job_type"),
            salary_package=data.get("salary_package"),
            eligible_branches=data.get("eligible_branches"),
            min_cgpa=min_cgpa,
            min_year=min_year,
            max_year=max_year,
            other_criteria=data.get("other_criteria"),
            application_deadline=app_deadline,
            drive_date=drive_date,
            vacancy_count=data.get("vacancy_count", 0),
            status=DriveStatus.PENDING,
        )
        db.session.add(drive)
        db.session.commit()

        return jsonify(
            {
                "id": drive.id,
                "job_title": drive.job_title,
                "status": drive.status,
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@company_bp.route("/drives", methods=["GET"])
@company_required
def get_drives():
    _, company = get_current_company()

    status_filter = request.args.get("status")
    query = PlacementDrive.query.filter_by(company_id=company.id)
    if status_filter in [
        DriveStatus.PENDING,
        DriveStatus.APPROVED,
        DriveStatus.CLOSED,
    ]:
        query = query.filter_by(status=status_filter)

    drives = query.all()
    result = []
    for d in drives:
        applicant_count = Application.query.filter_by(drive_id=d.id).count()
        shortlisted_count = Application.query.filter_by(
            drive_id=d.id, status=ApplicationStatus.SHORTLISTED
        ).count()
        selected_count = Application.query.filter_by(
            drive_id=d.id, status=ApplicationStatus.SELECTED
        ).count()

        result.append(
            {
                "id": d.id,
                "job_title": d.job_title,
                "status": d.status,
                "application_deadline": d.application_deadline.isoformat()
                if d.application_deadline
                else None,
                "applicant_count": applicant_count,
                "shortlisted_count": shortlisted_count,
                "selected_count": selected_count,
            }
        )

    return jsonify(result), 200


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@company_required
def get_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    applications = Application.query.filter_by(drive_id=drive.id).all()
    apps_data = []

    for app in applications:
        apps_data.append(
            {
                "application_id": app.id,
                "student_name": app.student.full_name,
                "roll_number": app.student.id,
                "branch": app.student.branch,
                "cgpa": app.student.cgpa,
                "year": app.student.year,
                "status": app.status,
                "applied_at": app.applied_at.isoformat()
                if app.applied_at
                else None,
                "resume_filename": app.student.resume_filename,
            }
        )

    return jsonify(
        {
            "id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "job_location": drive.job_location,
            "job_type": drive.job_type,
            "salary_package": drive.salary_package,
            "eligible_branches": drive.eligible_branches,
            "min_cgpa": drive.min_cgpa,
            "min_year": drive.min_year,
            "max_year": drive.max_year,
            "other_criteria": drive.other_criteria,
            "application_deadline": drive.application_deadline.isoformat()
            if drive.application_deadline
            else None,
            "drive_date": drive.drive_date.isoformat()
            if drive.drive_date
            else None,
            "vacancy_count": drive.vacancy_count,
            "status": drive.status,
            "applications": apps_data,
        }
    ), 200


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@company_required
def edit_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    if drive.status == DriveStatus.APPROVED:
        return jsonify({"message": "Cannot edit an approved drive"}), 400

    data = request.get_json()
    allowed_updates = [
        "job_description",
        "job_location",
        "salary_package",
        "other_criteria",
        "vacancy_count",
    ]
    for field in allowed_updates:
        if field in data:
            setattr(drive, field, data[field])

    if "drive_date" in data and data["drive_date"]:
        drive.drive_date = parse_iso_datetime(data["drive_date"])

    db.session.commit()
    return jsonify({"message": "Drive updated successfully"}), 200


@company_bp.route("/drives/<int:drive_id>/close", methods=["PATCH"])
@company_required
def close_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    drive.status = DriveStatus.CLOSED
    db.session.commit()

    return jsonify({"message": "Drive closed successfully"}), 200


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_required
def get_drive_applications(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    status_filter = request.args.get("status")
    query = Application.query.filter_by(drive_id=drive.id)
    if status_filter in [
        ApplicationStatus.APPLIED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
    ]:
        query = query.filter_by(status=status_filter)

    applications = query.all()
    apps_data = []

    for app in applications:
        apps_data.append(
            {
                "application_id": app.id,
                "student_name": app.student.full_name,
                "roll_number": app.student.id,
                "branch": app.student.branch,
                "cgpa": app.student.cgpa,
                "year": app.student.year,
                "skills": app.student.skills,
                "linkedin_url": app.student.linkedin_url,
                "status": app.status,
                "applied_at": app.applied_at.isoformat()
                if app.applied_at
                else None,
                "resume_filename": app.student.resume_filename,
            }
        )

    return jsonify(apps_data), 200


@company_bp.route(
    "/applications/<int:application_id>/status", methods=["PATCH"]
)
@company_required
def update_application_status(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in [
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
    ]:
        return jsonify({"message": "Invalid status"}), 400

    status_order = {
        ApplicationStatus.APPLIED: 0,
        ApplicationStatus.SHORTLISTED: 1,
        ApplicationStatus.SELECTED: 2,
        ApplicationStatus.REJECTED: -1,
    }

    if (
        new_status != ApplicationStatus.REJECTED
        and app_record.status != ApplicationStatus.REJECTED
    ):
        current_level = status_order.get(app_record.status, 0)
        new_level = status_order.get(new_status, 0)
        if (
            new_level <= current_level
            and app_record.status != ApplicationStatus.APPLIED
        ):
            return jsonify({"message": "Cannot move status backward"}), 400

    app_record.status = new_status

    if new_status == ApplicationStatus.SELECTED:
        app_record.student.is_placed = True

    db.session.commit()
    return jsonify({"message": "Application status updated successfully"}), 200


@company_bp.route(
    "/applications/<int:application_id>/interview", methods=["PATCH"]
)
@company_required
def update_application_interview(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    if app_record.status == ApplicationStatus.REJECTED:
        return jsonify(
            {"message": "Cannot schedule interview for rejected application"}
        ), 400

    data = request.get_json()

    try:
        if "interview_date" in data:
            interview_date = parse_iso_datetime(data["interview_date"])
            now = datetime.utcnow()
            if interview_date < now:
                return jsonify(
                    {"message": "interview_date must be in the future"}
                ), 400
            app_record.interview_date = interview_date

        if "interview_mode" in data:
            mode = data["interview_mode"]
            if mode not in ["Online", "Offline"]:
                return jsonify(
                    {"message": "interview_mode must be Online or Offline"}
                ), 400
            app_record.interview_mode = mode

        if "interview_link" in data:
            app_record.interview_link = data["interview_link"]

        if (
            app_record.interview_mode == "Online"
            and not app_record.interview_link
        ):
            return jsonify(
                {"message": "interview_link is required when mode is Online"}
            ), 400

    except Exception as e:
        return jsonify({"message": str(e)}), 400

    db.session.commit()
    return jsonify({"message": "Interview details updated successfully"}), 200


@company_bp.route("/applications/<int:application_id>/resume", methods=["GET"])
@company_required
def get_application_resume(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return jsonify({"message": "Access denied"}), 403

    filename = app_record.student.resume_filename
    if not filename:
        return jsonify({"message": "Student has no resume uploaded"}), 404

    upload_folder = os.path.join(
        current_app.root_path, "..", "static", "uploads", "resumes"
    )
    return send_from_directory(upload_folder, filename)
