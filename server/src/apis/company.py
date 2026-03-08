import os
from datetime import UTC, datetime

from flask import Blueprint, current_app, request, send_from_directory
from sqlalchemy import case, func
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
from src.helpers.cache import (
    cache,
    invalidate_application_cache,
    invalidate_company_cache,
    invalidate_drive_cache,
)
from src.helpers.utils import (
    error_response,
    parse_iso_datetime,
    success_response,
    validate_file,
)
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
        return error_response("Missing required fields")

    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already registered", 409)

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
        invalidate_company_cache()

        return success_response(
            "Registration successful. Awaiting admin approval.",
            status_code=201,
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {e!s}", 500)


@company_bp.route("/profile", methods=["GET"])
@company_required
@cache.cached(query_string=True)
def get_profile():
    _, company = get_current_company()
    if not company:
        return error_response("Company profile not found", 404)

    return success_response(
        "Profile fetched",
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
        },
    )


@company_bp.route("/profile", methods=["PUT"])
@company_required
def update_profile():
    _, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return error_response("Your company is pending admin approval", 403)

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

    try:
        db.session.commit()
        invalidate_company_cache()
        return success_response("Profile updated successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route("/profile/logo", methods=["POST"])
@company_required
def upload_logo():
    _, company = get_current_company()

    if "logo" not in request.files:
        return error_response("No file part")

    file = request.files["logo"]
    if file.filename == "":
        return error_response("No selected file")

    # Validate extension AND MIME type
    ok, reason = validate_file(
        file,
        LogoLimits.ALLOWED_LOGO_EXTENSIONS,
        LogoLimits.ALLOWED_LOGO_MIMETYPES,
    )
    if not ok:
        return error_response(reason)

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > LogoLimits.MAX_LOGO_SIZE:
        return error_response("File exceeds maximum size of 2MB")

    filename = secure_filename(file.filename)
    new_filename = f"{company.id}_{filename}"
    upload_folder = os.path.join(
        current_app.root_path,
        "..",
        "static",
        "uploads",
        "logos",
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, new_filename)
    file.save(file_path)

    company.logo_filename = new_filename
    try:
        db.session.commit()
        invalidate_company_cache()
        return success_response("Logo uploaded successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route("/dashboard", methods=["GET"])
@company_required
@cache.cached(query_string=True)
def get_dashboard():
    _, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return success_response(
            "Your company is pending admin approval",
            {"approval_status": company.approval_status},
        )

    drive_stats = (
        db.session.query(
            PlacementDrive.id.label("drive_id"),
            PlacementDrive.job_title,
            PlacementDrive.status,
            PlacementDrive.application_deadline,
            func.count(Application.id).label("applicant_count"),
            func.count(
                case(
                    (
                        Application.status == ApplicationStatus.SHORTLISTED,
                        1,
                    ),
                )
            ).label("shortlisted_count"),
            func.count(
                case(
                    (
                        Application.status == ApplicationStatus.SELECTED,
                        1,
                    ),
                )
            ).label("selected_count"),
        )
        .outerjoin(Application, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
        .group_by(PlacementDrive.id)
        .all()
    )

    drive_data = [
        {
            "drive_id": row.drive_id,
            "job_title": row.job_title,
            "status": row.status,
            "applicant_count": row.applicant_count,
            "shortlisted_count": row.shortlisted_count,
            "selected_count": row.selected_count,
            "deadline": (
                row.application_deadline.isoformat()
                if row.application_deadline
                else None
            ),
        }
        for row in drive_stats
    ]

    return success_response(
        "Dashboard fetched",
        {
            "approval_status": company.approval_status,
            "total_drives": len(drive_data),
            "drives": drive_data,
        },
    )


@company_bp.route("/drives", methods=["POST"])
@company_required
def create_drive():
    user, company = get_current_company()

    if company.approval_status != ApprovalStatus.APPROVED:
        return error_response("Company not approved", 403)

    if user.account_status == AccountStatus.BLACKLISTED:
        return error_response("Account blacklisted", 403)

    data = request.get_json()

    try:
        app_deadline = parse_iso_datetime(data["application_deadline"])
        now = datetime.now(UTC).replace(tzinfo=None)

        if app_deadline < now:
            return error_response(
                "application_deadline must be a future datetime"
            )
    except (KeyError, ValueError, TypeError):
        return error_response(
            "application_deadline is missing or invalid format"
        )

    min_cgpa = float(data.get("min_cgpa", 0.0))
    if not (0.0 <= min_cgpa <= 10.0):
        return error_response("min_cgpa must follow between 0.0 and 10.0")

    min_year = int(data.get("min_year", 1))
    max_year = int(data.get("max_year", 4))
    if min_year > max_year:
        return error_response("min_year must be <= max_year")

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
        invalidate_drive_cache()

        return success_response(
            "Drive created successfully",
            {
                "id": drive.id,
                "job_title": drive.job_title,
                "status": drive.status,
            },
            201,
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@company_bp.route("/drives", methods=["GET"])
@company_required
@cache.cached(query_string=True)
def get_drives():
    _, company = get_current_company()

    status_filter = request.args.get("status")

    drive_stats = (
        db.session.query(
            PlacementDrive.id,
            PlacementDrive.job_title,
            PlacementDrive.status,
            PlacementDrive.application_deadline,
            func.count(Application.id).label("applicant_count"),
            func.count(
                case(
                    (
                        Application.status == ApplicationStatus.SHORTLISTED,
                        1,
                    ),
                )
            ).label("shortlisted_count"),
            func.count(
                case(
                    (
                        Application.status == ApplicationStatus.SELECTED,
                        1,
                    ),
                )
            ).label("selected_count"),
        )
        .outerjoin(Application, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
    )

    if status_filter in [
        DriveStatus.PENDING,
        DriveStatus.APPROVED,
        DriveStatus.CLOSED,
    ]:
        drive_stats = drive_stats.filter(
            PlacementDrive.status == status_filter
        )

    rows = drive_stats.group_by(PlacementDrive.id).all()

    result = [
        {
            "id": row.id,
            "job_title": row.job_title,
            "status": row.status,
            "application_deadline": (
                row.application_deadline.isoformat()
                if row.application_deadline
                else None
            ),
            "applicant_count": row.applicant_count,
            "shortlisted_count": row.shortlisted_count,
            "selected_count": row.selected_count,
        }
        for row in rows
    ]

    return success_response("Drives fetched", result)


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@company_required
@cache.cached(query_string=True)
def get_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return error_response("Access denied", 403)

    applications = Application.query.filter_by(drive_id=drive.id).all()
    apps_data = [
        {
            "application_id": app.id,
            "student_name": app.student.full_name,
            "roll_number": app.student.id,
            "branch": app.student.branch,
            "cgpa": app.student.cgpa,
            "year": app.student.year,
            "status": app.status,
            "applied_at": (
                app.applied_at.isoformat() if app.applied_at else None
            ),
            "resume_filename": app.student.resume_filename,
        }
        for app in applications
    ]

    return success_response(
        "Drive fetched",
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
            "application_deadline": (
                drive.application_deadline.isoformat()
                if drive.application_deadline
                else None
            ),
            "drive_date": (
                drive.drive_date.isoformat() if drive.drive_date else None
            ),
            "vacancy_count": drive.vacancy_count,
            "status": drive.status,
            "applications": apps_data,
        },
    )


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@company_required
def edit_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return error_response("Access denied", 403)

    if drive.status == DriveStatus.APPROVED:
        return error_response("Cannot edit an approved drive")

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

    try:
        db.session.commit()
        invalidate_drive_cache()
        return success_response("Drive updated successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route("/drives/<int:drive_id>/close", methods=["PATCH"])
@company_required
def close_drive(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return error_response("Access denied", 403)

    drive.status = DriveStatus.CLOSED
    try:
        db.session.commit()
        invalidate_drive_cache()
        return success_response("Drive closed successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_required
@cache.cached(query_string=True)
def get_drive_applications(drive_id):
    _, company = get_current_company()
    drive = db.get_or_404(PlacementDrive, drive_id)

    if drive.company_id != company.id:
        return error_response("Access denied", 403)

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
    apps_data = [
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
            "applied_at": (
                app.applied_at.isoformat() if app.applied_at else None
            ),
            "resume_filename": app.student.resume_filename,
        }
        for app in applications
    ]

    return success_response("Applications fetched", apps_data)


@company_bp.route(
    "/applications/<int:application_id>/status",
    methods=["PATCH"],
)
@company_required
def update_application_status(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return error_response("Access denied", 403)

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in [
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
    ]:
        return error_response("Invalid status")

    ok, reason = app_record.can_transition_to(new_status)
    if not ok:
        return error_response(reason)

    app_record.status = new_status

    if new_status == ApplicationStatus.SELECTED:
        app_record.student.is_placed = True

    try:
        db.session.commit()
        invalidate_application_cache()
        return success_response("Application status updated successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route(
    "/applications/<int:application_id>/interview",
    methods=["PATCH"],
)
@company_required
def update_application_interview(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return error_response("Access denied", 403)

    if app_record.status == ApplicationStatus.REJECTED:
        return error_response(
            "Cannot schedule interview for rejected application"
        )

    data = request.get_json()

    try:
        if "interview_date" in data:
            interview_date = parse_iso_datetime(data["interview_date"])
            now = datetime.now(UTC).replace(tzinfo=None)
            if interview_date < now:
                return error_response("interview_date must be in the future")
            app_record.interview_date = interview_date

        if "interview_mode" in data:
            mode = data["interview_mode"]
            if mode not in ["Online", "Offline"]:
                return error_response(
                    "interview_mode must be Online or Offline"
                )
            app_record.interview_mode = mode

        if "interview_link" in data:
            app_record.interview_link = data["interview_link"]

        if (
            app_record.interview_mode == "Online"
            and not app_record.interview_link
        ):
            return error_response(
                "interview_link is required when mode is Online"
            )

    except Exception as e:
        return error_response(str(e))

    try:
        db.session.commit()
        invalidate_application_cache()
        return success_response("Interview details updated successfully")
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@company_bp.route(
    "/applications/<int:application_id>/resume",
    methods=["GET"],
)
@company_required
@cache.cached(query_string=True)
def get_application_resume(application_id):
    _, company = get_current_company()
    app_record = db.get_or_404(Application, application_id)

    if app_record.drive.company_id != company.id:
        return error_response("Access denied", 403)

    filename = app_record.student.resume_filename
    if not filename:
        return error_response("Student has no resume uploaded", 404)

    upload_folder = os.path.join(
        current_app.root_path,
        "..",
        "static",
        "uploads",
        "resumes",
    )
    return send_from_directory(upload_folder, filename)
