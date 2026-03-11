from flask import Blueprint, request
from sqlalchemy import func
from werkzeug.exceptions import NotFound

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    ApprovalStatus,
    DriveStatus,
)
from src.helpers.auth import admin_required, roles_required
from src.helpers.cache import (
    cache,
    invalidate_application_cache,
    invalidate_company_cache,
    invalidate_drive_cache,
    invalidate_student_cache,
)
from src.helpers.utils import error_response, escape_like, success_response
from src.jobs.tasks import send_monthly_placement_report
from src.models import Application, Company, PlacementDrive, Student, User, db

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _get_company_stats() -> dict:
    """Return aggregate company counts by approval status."""
    companies_query = Company.query
    return {
        "total": companies_query.count(),
        "pending": companies_query.filter_by(
            approval_status=ApprovalStatus.PENDING
        ).count(),
        "approved": companies_query.filter_by(
            approval_status=ApprovalStatus.APPROVED
        ).count(),
        "rejected": companies_query.filter_by(
            approval_status=ApprovalStatus.REJECTED
        ).count(),
    }


def _get_drive_stats() -> dict:
    """Return aggregate drive counts by status."""
    drives_query = PlacementDrive.query
    return {
        "total": drives_query.count(),
        "pending": drives_query.filter_by(status=DriveStatus.PENDING).count(),
        "approved": drives_query.filter_by(
            status=DriveStatus.APPROVED
        ).count(),
        "rejected": drives_query.filter_by(
            status=DriveStatus.REJECTED
        ).count(),
    }


def _get_recent_placements() -> list[dict]:
    """Return the 5 most recent selected applications."""
    recent = (
        Application.query.filter_by(status=ApplicationStatus.SELECTED)
        .join(Student)
        .join(PlacementDrive)
        .join(Company)
        .order_by(Application.updated_at.desc())
        .limit(5)
        .all()
    )
    return [
        {
            "student_name": app.student.full_name,
            "student_id": app.student.id,
            "student_branch": app.student.branch,
            "company_name": app.drive.company.company_name,
            "company_id": app.drive.company.id,
            "drive_id": app.drive.id,
            "role": app.drive.job_title,
            "package": app.drive.salary_package,
            "date": (app.updated_at.isoformat() if app.updated_at else None),
        }
        for app in recent
    ]


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_dashboard():
    try:
        return success_response(
            "Dashboard data fetched successfully",
            {
                "total_students": Student.query.count(),
                "total_applications": Application.query.count(),
                "companies": _get_company_stats(),
                "drives": _get_drive_stats(),
                "recent_placements": _get_recent_placements(),
            },
        )
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/companies", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_companies():
    try:
        status_filter = request.args.get("status")
        search_query = request.args.get("search")

        drive_count_sq = (
            db.session.query(
                PlacementDrive.company_id,
                func.count(PlacementDrive.id).label("drive_count"),
            )
            .group_by(PlacementDrive.company_id)
            .subquery()
        )

        query = (
            db.session.query(Company, User, drive_count_sq.c.drive_count)
            .join(User, Company.user_id == User.id)
            .outerjoin(
                drive_count_sq,
                Company.id == drive_count_sq.c.company_id,
            )
        )

        if status_filter in [
            ApprovalStatus.PENDING,
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
        ]:
            query = query.filter(Company.approval_status == status_filter)

        if search_query:
            term = f"%{escape_like(search_query)}%"
            query = query.filter(
                (Company.company_name.ilike(term, escape="\\"))
                | (Company.industry.ilike(term, escape="\\"))
            )

        rows = query.all()

        result_data = [
            {
                "id": company.id,
                "company_name": company.company_name,
                "approval_status": company.approval_status,
                "email": user.email,
                "drive_count": drive_count or 0,
                "industry": company.industry,
                "hr_name": company.hr_name,
                "hr_contact": company.hr_contact,
                "account_status": user.account_status,
                "created_at": (
                    company.created_at.isoformat()
                    if company.created_at
                    else None
                ),
            }
            for company, user, drive_count in rows
        ]

        return success_response("Companies fetched successfully", result_data)
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/companies/<int:company_id>", methods=["GET"])
@roles_required("admin", "student")
@cache.cached(query_string=True)
def get_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)

        user = company.user
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        drives_data = [
            {
                "id": d.id,
                "job_title": d.job_title,
                "job_type": d.job_type,
                "salary_package": d.salary_package,
                "status": d.status,
                "application_deadline": (
                    d.application_deadline.isoformat()
                    if d.application_deadline
                    else None
                ),
            }
            for d in drives
        ]

        return success_response(
            "Company fetched successfully",
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
                "rejection_reason": company.rejection_reason,
                "account_status": user.account_status,
                "drives": drives_data,
            },
        )
    except NotFound:
        raise
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/companies/<int:company_id>/approve", methods=["PATCH"])
@admin_required
def approve_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        if company.approval_status == ApprovalStatus.APPROVED:
            return error_response("Company is already approved", 409)

        company.approval_status = ApprovalStatus.APPROVED
        db.session.commit()
        invalidate_company_cache()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Company approved successfully",
            {
                "id": company.id,
                "approval_status": company.approval_status,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/companies/<int:company_id>/reject", methods=["PATCH"])
@admin_required
def reject_company(company_id):
    try:
        data = request.get_json()
        if not data or "reason" not in data:
            return error_response("Rejection reason is required")

        company = db.get_or_404(Company, company_id)
        if company.approval_status == ApprovalStatus.REJECTED:
            return error_response("Company is already rejected", 409)

        company.approval_status = ApprovalStatus.REJECTED
        company.rejection_reason = data["reason"]
        db.session.commit()
        invalidate_company_cache()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Company rejected successfully",
            {
                "id": company.id,
                "approval_status": company.approval_status,
                "rejection_reason": company.rejection_reason,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["PATCH"])
@admin_required
def blacklist_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        user = db.get_or_404(User, company.user_id)

        if user.account_status == AccountStatus.BLACKLISTED:
            return error_response("Account is already blacklisted", 409)

        user.account_status = AccountStatus.BLACKLISTED
        db.session.commit()
        invalidate_company_cache()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Company blacklisted successfully",
            {
                "company_id": company.id,
                "account_status": user.account_status,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/companies/<int:company_id>/activate", methods=["PATCH"])
@admin_required
def activate_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        user = db.get_or_404(User, company.user_id)

        if user.account_status == AccountStatus.ACTIVE:
            return error_response("Account is already active", 409)

        user.account_status = AccountStatus.ACTIVE
        db.session.commit()
        invalidate_company_cache()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Company account activated successfully",
            {
                "company_id": company.id,
                "account_status": user.account_status,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/students", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_students():
    try:
        search_query = request.args.get("search")
        branch_filter = request.args.get("branch")
        is_placed_filter = request.args.get("is_placed")

        query = db.session.query(Student, User).join(
            User, Student.user_id == User.id
        )

        if search_query:
            term = f"%{escape_like(search_query)}%"
            query = query.filter(
                (Student.full_name.ilike(term, escape="\\"))
                | (User.email.ilike(term, escape="\\"))
            )

        if branch_filter:
            query = query.filter(Student.branch == branch_filter)

        if is_placed_filter is not None:
            is_placed = is_placed_filter.lower() == "true"
            query = query.filter(Student.is_placed == is_placed)

        students = query.all()

        result_data = [
            {
                "id": student.id,
                "name": student.full_name,
                "email": user.email,
                "branch": student.branch,
                "cgpa": student.cgpa,
                "year": student.year,
                "is_placed": student.is_placed,
                "account_status": user.account_status,
            }
            for student, user in students
        ]

        return success_response("Students fetched successfully", result_data)
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/students/<int:student_id>", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)

        applications = (
            Application.query.filter_by(student_id=student.id)
            .join(PlacementDrive)
            .join(Company)
            .all()
        )
        apps_data = [
            {
                "id": app.id,
                "drive_title": app.drive.job_title,
                "company_name": app.drive.company.company_name,
                "status": app.status,
                "applied_at": (
                    app.applied_at.isoformat() if app.applied_at else None
                ),
            }
            for app in applications
        ]

        return success_response(
            "Student fetched successfully",
            {
                "id": student.id,
                "student_id": student.id,
                "name": student.full_name,
                "full_name": student.full_name,
                "email": student.user.email if student.user else None,
                "phone": student.phone,
                "branch": student.branch,
                "year": student.year,
                "cgpa": float(student.cgpa)
                if student.cgpa is not None
                else None,
                "gender": student.gender,
                "date_of_birth": student.date_of_birth.isoformat()
                if student.date_of_birth
                else None,
                "address": student.address,
                "linkedin_url": student.linkedin_url,
                "github_url": student.github_url,
                "skills": student.skills,
                "resume_filename": student.resume_filename,
                "is_placed": student.is_placed,
                "account_status": student.user.account_status
                if student.user
                else None,
                "user_id": student.user_id,
                "applications": apps_data,
            },
        )
    except NotFound:
        raise
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/students/<int:student_id>/blacklist", methods=["PATCH"])
@admin_required
def blacklist_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)
        user = db.get_or_404(User, student.user_id)

        if user.account_status == AccountStatus.BLACKLISTED:
            return error_response("Account is already blacklisted", 409)

        user.account_status = AccountStatus.BLACKLISTED
        db.session.commit()
        invalidate_student_cache()
        invalidate_application_cache()

        return success_response(
            "Student blacklisted successfully",
            {
                "student_id": student.id,
                "account_status": user.account_status,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/students/<int:student_id>/activate", methods=["PATCH"])
@admin_required
def activate_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)
        user = db.get_or_404(User, student.user_id)

        if user.account_status == AccountStatus.ACTIVE:
            return error_response("Account is already active", 409)

        user.account_status = AccountStatus.ACTIVE
        db.session.commit()
        invalidate_student_cache()
        invalidate_application_cache()

        return success_response(
            "Student account activated successfully",
            {
                "student_id": student.id,
                "account_status": user.account_status,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/drives", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_drives():
    try:
        status_filter = request.args.get("status")
        search_query = request.args.get("search")

        app_count_sq = (
            db.session.query(
                Application.drive_id,
                func.count(Application.id).label("applicant_count"),
            )
            .group_by(Application.drive_id)
            .subquery()
        )

        query = (
            db.session.query(
                PlacementDrive,
                func.coalesce(app_count_sq.c.applicant_count, 0).label(
                    "applicant_count"
                ),
            )
            .join(Company)
            .outerjoin(
                app_count_sq,
                PlacementDrive.id == app_count_sq.c.drive_id,
            )
        )

        if status_filter in [
            DriveStatus.PENDING,
            DriveStatus.APPROVED,
            DriveStatus.CLOSED,
        ]:
            query = query.filter(PlacementDrive.status == status_filter)

        if search_query:
            term = f"%{escape_like(search_query)}%"
            query = query.filter(
                (PlacementDrive.job_title.ilike(term, escape="\\"))
                | (Company.company_name.ilike(term, escape="\\"))
            )

        rows = query.all()

        result_data = [
            {
                "id": drive.id,
                "job_title": drive.job_title,
                "company_name": drive.company.company_name,
                "status": drive.status,
                "application_deadline": (
                    drive.application_deadline.isoformat()
                ),
                "applicant_count": applicant_count,
                "job_type": drive.job_type,
                "salary_package": drive.salary_package,
                "eligible_branches": drive.eligible_branches,
                "min_cgpa": drive.min_cgpa,
                "other_criteria": drive.other_criteria,
            }
            for drive, applicant_count in rows
        ]

        return success_response("Drives fetched successfully", result_data)
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/drives/<int:drive_id>", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_drive(drive_id):
    try:
        drive = db.get_or_404(PlacementDrive, drive_id)

        applications = (
            Application.query.filter_by(drive_id=drive.id).join(Student).all()
        )
        apps_data = [
            {
                "id": app.id,
                "student_name": app.student.full_name,
                "student_id": app.student.id,
                "status": app.status,
            }
            for app in applications
        ]

        return success_response(
            "Drive fetched successfully",
            {
                "id": drive.id,
                "company_id": drive.company_id,
                "job_title": drive.job_title,
                "job_type": drive.job_type,
                "description": drive.job_description,
                "job_location": drive.job_location,
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
                "vacancy_count": drive.vacancy_count,
                "status": drive.status,
                "company_name": drive.company.company_name,
                "company_description": drive.company.description,
                "applications": apps_data,
            },
        )
    except NotFound:
        raise
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["PATCH"])
@admin_required
def approve_drive(drive_id):
    try:
        drive = db.get_or_404(PlacementDrive, drive_id)
        if drive.status == DriveStatus.APPROVED:
            return error_response("Drive is already approved", 409)

        drive.status = DriveStatus.APPROVED
        db.session.commit()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Drive approved successfully",
            {"id": drive.id, "status": drive.status},
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["PATCH"])
@admin_required
def reject_drive(drive_id):
    try:
        data = request.get_json()
        if not data or "reason" not in data:
            return error_response("Rejection reason is required")

        drive = db.get_or_404(PlacementDrive, drive_id)
        if drive.status == DriveStatus.REJECTED:
            return error_response("Drive is already rejected", 409)

        drive.status = DriveStatus.REJECTED
        drive.rejection_reason = data["reason"]
        db.session.commit()
        invalidate_drive_cache()
        invalidate_application_cache()

        return success_response(
            "Drive rejected successfully",
            {
                "id": drive.id,
                "status": drive.status,
                "rejection_reason": drive.rejection_reason,
            },
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@admin_bp.route("/applications", methods=["GET"])
@admin_required
@cache.cached(query_string=True)
def get_applications():
    try:
        status_filter = request.args.get("status")
        drive_filter = request.args.get("drive_id")
        company_filter = request.args.get("company_id")

        query = (
            db.session.query(Application)
            .join(PlacementDrive)
            .join(Company)
            .join(Student)
        )

        if status_filter:
            query = query.filter(Application.status == status_filter)

        if drive_filter:
            query = query.filter(Application.drive_id == drive_filter)

        if company_filter:
            query = query.filter(PlacementDrive.company_id == company_filter)

        applications = query.all()

        result_data = [
            {
                "id": app.id,
                "student_id": app.student_id,
                "student_name": app.student.full_name,
                "student_branch": app.student.branch,
                "student_year": app.student.year,
                "drive_id": app.drive_id,
                "drive_title": app.drive.job_title,
                "company_id": app.drive.company_id,
                "company_name": app.drive.company.company_name,
                "status": app.status,
                "applied_at": (
                    app.applied_at.isoformat() if app.applied_at else None
                ),
            }
            for app in applications
        ]

        return success_response(
            "Applications fetched successfully", result_data
        )
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route("/reports/generate", methods=["POST"])
@admin_required
def generate_report():
    """Trigger monthly placement report generation asynchronously."""
    send_monthly_placement_report.delay()
    return success_response(
        "Report generation started. You will receive it via email shortly."
    )
