import os
from datetime import UTC, datetime

from flask import Blueprint, current_app, request, send_from_directory, url_for
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    DriveStatus,
    ExportJobStatus,
    ResumeLimits,
    UserRole,
)
from src.helpers.auth import get_current_student, student_required
from src.helpers.student_helpers import check_eligibility
from src.helpers.utils import (
    error_response,
    escape_like,
    success_response,
    validate_file,
)
from src.jobs.tasks import export_student_applications_csv
from src.models import (
    Application,
    Company,
    ExportJob,
    PlacementDrive,
    Student,
    User,
    db,
)

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


def _serialize_profile(student: Student, user: User) -> dict:
    return {
        "student_id": student.id,
        "email": user.email,
        "full_name": student.full_name,
        "branch": student.branch,
        "year": student.year,
        "cgpa": student.cgpa,
        "phone": student.phone,
        "gender": student.gender,
        "date_of_birth": (
            student.date_of_birth.isoformat()
            if student.date_of_birth
            else None
        ),
        "address": student.address,
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "skills": student.skills,
        "resume_filename": student.resume_filename,
        "profile_picture": student.profile_picture,
        "is_placed": student.is_placed,
        "account_status": user.account_status,
    }


@student_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    required = [
        "email",
        "password",
        "full_name",
        "branch",
        "year",
        "cgpa",
        "phone",
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}")

    # Validate cgpa
    try:
        cgpa = float(data["cgpa"])
    except (ValueError, TypeError):
        return error_response("cgpa must be a number")
    if not (0.0 <= cgpa <= 10.0):
        return error_response("cgpa must be between 0.0 and 10.0")

    # Validate year
    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return error_response("year must be an integer")
    if not (1 <= year <= 4):
        return error_response("year must be between 1 and 4")

    # Check duplicate email
    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already exists", 409)

    try:
        user = User(
            email=data["email"],
            role=UserRole.STUDENT,
            account_status=AccountStatus.ACTIVE,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            full_name=data["full_name"],
            branch=data["branch"],
            year=year,
            cgpa=cgpa,
            phone=data.get("phone"),
        )
        db.session.add(student)
        db.session.commit()

        return success_response(
            "Registration successful. You can now log in.",
            status_code=201,
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {e!s}", 500)


# ─── Profile ─────────────────────────────────────────────────


@student_bp.route("/profile", methods=["GET"])
@student_required
def get_profile():
    user, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    return success_response(
        "Profile fetched",
        _serialize_profile(student, user),
    )


@student_bp.route("/profile", methods=["PUT"])
@student_required
def update_profile():
    user, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body is required")

    allowed_updates = [
        "full_name",
        "phone",
        "gender",
        "date_of_birth",
        "address",
        "linkedin_url",
        "github_url",
        "skills",
        "year",
        "cgpa",
    ]

    # Validate cgpa if provided
    if "cgpa" in data:
        try:
            cgpa = float(data["cgpa"])
        except (ValueError, TypeError):
            return error_response("cgpa must be a number")
        if not (0.0 <= cgpa <= 10.0):
            return error_response("cgpa must be between 0.0 and 10.0")
        data["cgpa"] = cgpa

    # Validate year if provided
    if "year" in data:
        try:
            year = int(data["year"])
        except (ValueError, TypeError):
            return error_response("year must be an integer")
        if not (1 <= year <= 4):
            return error_response("year must be between 1 and 4")
        data["year"] = year

    for field in allowed_updates:
        if field in data:
            setattr(student, field, data[field])

    try:
        db.session.commit()
        return success_response(
            "Profile updated successfully",
            _serialize_profile(student, user),
        )
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@student_bp.route("/profile/resume", methods=["POST"])
@student_required
def upload_resume():
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    if "resume" not in request.files:
        return error_response("No resume file provided")

    file = request.files["resume"]
    if file.filename == "":
        return error_response("No selected file")

    # Validate extension AND MIME type
    ok, reason = validate_file(
        file,
        ResumeLimits.ALLOWED_EXTENSIONS,
        ResumeLimits.ALLOWED_MIMETYPES,
    )
    if not ok:
        return error_response(reason)

    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > ResumeLimits.MAX_SIZE:
        return error_response("File exceeds maximum size of 5MB")

    filename = secure_filename(file.filename)
    new_filename = f"{student.id}_{filename}"
    upload_folder = os.path.join(
        current_app.root_path,
        "..",
        "static",
        "uploads",
        "resumes",
    )
    os.makedirs(upload_folder, exist_ok=True)

    # Delete old resume if exists
    if student.resume_filename:
        old_path = os.path.join(upload_folder, student.resume_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    file_path = os.path.join(upload_folder, new_filename)
    file.save(file_path)

    student.resume_filename = new_filename
    try:
        db.session.commit()
        return success_response(
            "Resume uploaded successfully",
            {"resume_filename": new_filename},
        )
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@student_bp.route("/profile/resume", methods=["GET"])
@student_required
def download_resume():
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    if not student.resume_filename:
        return error_response("No resume uploaded yet", 404)

    upload_folder = os.path.join(
        current_app.root_path,
        "..",
        "static",
        "uploads",
        "resumes",
    )
    return send_from_directory(upload_folder, student.resume_filename)


@student_bp.route("/dashboard", methods=["GET"])
@student_required
def get_dashboard():
    user, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    # Profile summary
    profile_summary = {
        "full_name": student.full_name,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year,
        "is_placed": student.is_placed,
    }

    # Application counts
    applications = Application.query.filter_by(student_id=student.id).all()
    total_applications = len(applications)
    breakdown = {
        "applied": 0,
        "shortlisted": 0,
        "selected": 0,
        "rejected": 0,
    }
    for app in applications:
        if app.status in breakdown:
            breakdown[app.status] += 1

    # Upcoming interviews
    now = datetime.now(UTC).replace(tzinfo=None)
    upcoming = []
    for app in applications:
        if app.interview_date and app.interview_date > now:
            drive = app.drive
            upcoming.append(
                {
                    "drive_title": drive.job_title,
                    "company_name": (drive.company.company_name),
                    "interview_date": (app.interview_date.isoformat()),
                    "interview_mode": app.interview_mode,
                    "interview_link": app.interview_link,
                }
            )
    upcoming.sort(key=lambda x: x["interview_date"])

    # Eligible drives not yet applied to
    applied_drive_ids = {app.drive_id for app in applications}
    eligible_drives = PlacementDrive.query.filter(
        PlacementDrive.status == DriveStatus.APPROVED,
        PlacementDrive.application_deadline > now,
    ).all()
    eligible_not_applied = 0
    for drive in eligible_drives:
        if drive.id not in applied_drive_ids:
            is_eligible, _ = check_eligibility(student, drive)
            if is_eligible:
                eligible_not_applied += 1

    return success_response(
        "Dashboard fetched",
        {
            "profile": profile_summary,
            "total_applications": total_applications,
            "applications_breakdown": breakdown,
            "upcoming_interviews": upcoming,
            "eligible_drives_not_applied": (eligible_not_applied),
        },
    )


@student_bp.route("/drives", methods=["GET"])
@student_required
def get_drives():
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    now = datetime.now(UTC).replace(tzinfo=None)

    query = PlacementDrive.query.filter(
        PlacementDrive.status == DriveStatus.APPROVED,
        PlacementDrive.application_deadline > now,
    )

    # Filters
    search = request.args.get("search")
    if search:
        term = f"%{escape_like(search)}%"
        query = query.join(Company).filter(
            or_(
                PlacementDrive.job_title.ilike(term, escape="\\"),
                Company.company_name.ilike(term, escape="\\"),
            )
        )

    job_type = request.args.get("job_type")
    if job_type:
        query = query.filter(PlacementDrive.job_type == job_type)

    drives = query.all()

    # Get student's applied drive ids
    applied_drive_ids = {
        a.drive_id
        for a in Application.query.filter_by(student_id=student.id).all()
    }

    result = []
    for drive in drives:
        is_eligible, _ = check_eligibility(student, drive)
        has_applied = drive.id in applied_drive_ids

        # Filter eligible_only
        eligible_only = request.args.get("eligible_only")
        if eligible_only == "true" and not is_eligible:
            continue

        # Filter not_applied
        not_applied = request.args.get("not_applied")
        if not_applied == "true" and has_applied:
            continue

        result.append(
            {
                "drive_id": drive.id,
                "job_title": drive.job_title,
                "company_name": (drive.company.company_name),
                "company_logo": (drive.company.logo_filename),
                "job_type": drive.job_type,
                "job_location": drive.job_location,
                "salary_package": drive.salary_package,
                "application_deadline": (
                    drive.application_deadline.isoformat()
                    if drive.application_deadline
                    else None
                ),
                "drive_date": (
                    drive.drive_date.isoformat() if drive.drive_date else None
                ),
                "vacancy_count": drive.vacancy_count,
                "has_applied": has_applied,
                "is_eligible": is_eligible,
            }
        )

    return success_response("Drives fetched", result)


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@student_required
def get_drive_detail(drive_id):
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    drive = db.session.get(PlacementDrive, drive_id)
    if not drive or drive.status != DriveStatus.APPROVED:
        return error_response("Drive not found", 404)

    is_eligible, _ = check_eligibility(student, drive)

    # Check if student has applied
    application = Application.query.filter_by(
        student_id=student.id, drive_id=drive.id
    ).first()
    has_applied = application is not None

    app_data = None
    if application:
        app_data = {
            "application_id": application.id,
            "status": application.status,
            "applied_at": (
                application.applied_at.isoformat()
                if application.applied_at
                else None
            ),
            "interview_date": (
                application.interview_date.isoformat()
                if application.interview_date
                else None
            ),
            "interview_mode": application.interview_mode,
            "interview_link": application.interview_link,
        }

    company = drive.company
    data = {
        "drive_id": drive.id,
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
        "result_date": (
            drive.result_date.isoformat() if drive.result_date else None
        ),
        "vacancy_count": drive.vacancy_count,
        "company_name": company.company_name,
        "company_website": company.website,
        "company_industry": company.industry,
        "company_logo": company.logo_filename,
        "has_applied": has_applied,
        "is_eligible": is_eligible,
        "application": app_data,
    }

    return success_response("Drive fetched", data)


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_to_drive(drive_id):
    user, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    # Check blacklisted
    if user.account_status == AccountStatus.BLACKLISTED:
        return error_response("Your account is blacklisted", 403)

    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        return error_response("Drive not found", 404)

    if drive.status != DriveStatus.APPROVED:
        return error_response("This drive is not accepting applications")

    # Check deadline
    now = datetime.now(UTC).replace(tzinfo=None)
    if drive.application_deadline < now:
        return error_response("Application deadline has passed")

    # Check eligibility
    is_eligible, reason = check_eligibility(student, drive)
    if not is_eligible:
        return error_response(reason, 403)

    # Check duplicate
    existing = Application.query.filter_by(
        student_id=student.id, drive_id=drive.id
    ).first()
    if existing:
        return error_response("You have already applied to this drive", 409)

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status=ApplicationStatus.APPLIED,
    )
    db.session.add(application)
    try:
        db.session.commit()
        return success_response(
            "Application submitted successfully.",
            {
                "application_id": application.id,
                "drive_id": drive.id,
                "status": application.status,
                "applied_at": (
                    application.applied_at.isoformat()
                    if application.applied_at
                    else None
                ),
            },
            201,
        )
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)


@student_bp.route("/applications", methods=["GET"])
@student_required
def get_applications():
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    query = Application.query.filter_by(student_id=student.id)

    # Filter by status
    status_filter = request.args.get("status")
    if status_filter in [
        ApplicationStatus.APPLIED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
    ]:
        query = query.filter_by(status=status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()

    result = [
        {
            "application_id": app.id,
            "drive_id": app.drive.id,
            "job_title": app.drive.job_title,
            "company_name": app.drive.company.company_name,
            "job_type": app.drive.job_type,
            "salary_package": app.drive.salary_package,
            "status": app.status,
            "applied_at": (
                app.applied_at.isoformat() if app.applied_at else None
            ),
            "interview_date": (
                app.interview_date.isoformat() if app.interview_date else None
            ),
            "interview_mode": app.interview_mode,
            "interview_link": app.interview_link,
            "company_remarks": app.company_remarks,
        }
        for app in applications
    ]

    return success_response("Applications fetched", result)


@student_bp.route("/applications/<int:application_id>", methods=["GET"])
@student_required
def get_application_detail(application_id):
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    application = db.session.get(Application, application_id)
    if not application:
        return error_response("Application not found", 404)

    if application.student_id != student.id:
        return error_response("Access denied", 403)

    drive = application.drive
    company = drive.company

    data = {
        "application_id": application.id,
        "status": application.status,
        "applied_at": (
            application.applied_at.isoformat()
            if application.applied_at
            else None
        ),
        "interview_date": (
            application.interview_date.isoformat()
            if application.interview_date
            else None
        ),
        "interview_mode": application.interview_mode,
        "interview_link": application.interview_link,
        "company_remarks": application.company_remarks,
        "offer_letter_url": application.offer_letter_url,
        "drive": {
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "job_location": drive.job_location,
            "job_type": drive.job_type,
            "salary_package": drive.salary_package,
            "application_deadline": (
                drive.application_deadline.isoformat()
                if drive.application_deadline
                else None
            ),
            "drive_date": (
                drive.drive_date.isoformat() if drive.drive_date else None
            ),
            "vacancy_count": drive.vacancy_count,
        },
        "company": {
            "company_name": company.company_name,
            "website": company.website,
            "industry": company.industry,
            "logo_filename": company.logo_filename,
        },
    }

    return success_response("Application fetched", data)


@student_bp.route("/applications/export", methods=["POST"])
@student_required
def export_applications():
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    # Create export job in queued state
    export_job = ExportJob(
        student_id=student.id,
        status=ExportJobStatus.QUEUED,
    )
    db.session.add(export_job)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response("Database error. Please try again.", 500)

    # Dispatch async Celery task
    export_student_applications_csv.delay(student.id, export_job.id)

    return success_response(
        "Export started. You will be notified when ready.",
        {"export_job_id": export_job.id},
        202,
    )


@student_bp.route(
    "/applications/export/<int:job_id>",
    methods=["GET"],
)
@student_required
def get_export_status(job_id):
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    export_job = db.session.get(ExportJob, job_id)
    if not export_job:
        return error_response("Export job not found", 404)

    if export_job.student_id != student.id:
        return error_response("Access denied", 403)

    data = {
        "job_id": export_job.id,
        "status": export_job.status,
        "created_at": (
            export_job.created_at.isoformat()
            if export_job.created_at
            else None
        ),
        "completed_at": (
            export_job.completed_at.isoformat()
            if export_job.completed_at
            else None
        ),
    }

    if export_job.status == ExportJobStatus.DONE:
        data["download_url"] = url_for(
            "student.download_export",
            job_id=export_job.id,
            _external=True,
        )

    return success_response("Export status fetched", data)


@student_bp.route(
    "/applications/export/<int:job_id>/download",
    methods=["GET"],
)
@student_required
def download_export(job_id):
    _, student = get_current_student()
    if not student:
        return error_response("Student profile not found", 404)

    export_job = db.session.get(ExportJob, job_id)
    if not export_job:
        return error_response("Export job not found", 404)

    if export_job.student_id != student.id:
        return error_response("Access denied", 403)

    if export_job.status != ExportJobStatus.DONE:
        return error_response("Export is not ready for download")

    export_folder = os.path.join(
        current_app.root_path,
        "..",
        "static",
        "uploads",
        "exports",
    )
    return send_from_directory(
        export_folder,
        export_job.file_path,
        as_attachment=True,
    )
