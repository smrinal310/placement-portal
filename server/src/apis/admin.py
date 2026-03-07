from flask import Blueprint, jsonify, request

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    ApprovalStatus,
    DriveStatus,
)
from src.helpers.auth import admin_required
from src.models import Application, Company, PlacementDrive, Student, User, db

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def get_dashboard():
    try:
        total_students = Student.query.count()
        total_applications = Application.query.count()

        # Get Companies
        companies_query = Company.query
        total_companies = companies_query.count()
        pending_companies = companies_query.filter_by(
            approval_status=ApprovalStatus.PENDING
        ).count()
        approved_companies = companies_query.filter_by(
            approval_status=ApprovalStatus.APPROVED
        ).count()
        rejected_companies = companies_query.filter_by(
            approval_status=ApprovalStatus.REJECTED
        ).count()

        # Get Drives
        drives_query = PlacementDrive.query
        total_drives = drives_query.count()
        pending_drives = drives_query.filter_by(
            status=DriveStatus.PENDING
        ).count()
        approved_drives = drives_query.filter_by(
            status=DriveStatus.APPROVED
        ).count()
        rejected_drives = drives_query.filter_by(
            status=DriveStatus.REJECTED
        ).count()

        # Recent Placements (Top 5 Selected Applications)
        recent_placements_query = (
            Application.query.filter_by(status=ApplicationStatus.SELECTED)
            .join(Student)
            .join(PlacementDrive)
            .join(Company)
            .order_by(Application.updated_at.desc())
            .limit(5)
            .all()
        )
        recent_placements = [
            {
                "student_name": app.student.full_name,
                "company_name": app.drive.company.company_name,
                "role": app.drive.job_title,
                "package": app.drive.salary_package,
                "date": app.updated_at.isoformat() if app.updated_at else None,
            }
            for app in recent_placements_query
        ]

        # Recent Activity Feed
        # We'll merge the 5 most recent Companies, Drives, and Applications,
        # then sort and take top 5
        recent_companies = (
            Company.query.order_by(Company.created_at.desc()).limit(5).all()
        )
        recent_drives = (
            PlacementDrive.query.order_by(PlacementDrive.created_at.desc())
            .limit(5)
            .all()
        )
        recent_apps = (
            Application.query.order_by(Application.created_at.desc())
            .limit(5)
            .all()
        )

        activities = []
        for c in recent_companies:
            activities.append(
                {
                    "type": "company_registered",
                    "title": c.company_name,
                    "description": "Registered for campus drive.",
                    "timestamp": c.created_at,
                }
            )
        for d in recent_drives:
            activities.append(
                {
                    "type": "drive_added",
                    "title": d.company.company_name
                    if d.company
                    else "Unknown Company",
                    "description": (
                        f"New Placement Drive added: {d.job_title}."
                    ),
                    "timestamp": d.created_at,
                }
            )
        for a in recent_apps:
            action = (
                "Applied for role"
                if a.status == ApplicationStatus.APPLIED
                else f"Application {a.status}"
            )
            if a.status == ApplicationStatus.SELECTED:
                company_name = (
                    a.drive.company.company_name
                    if a.drive and a.drive.company
                    else "Company"
                )
                action = f"Accepted offer from {company_name}"
            activities.append(
                {
                    "type": "student_applied",
                    "title": a.student.full_name
                    if a.student
                    else "Unknown Student",
                    "description": action,
                    "timestamp": a.created_at,
                }
            )

        # Sort activities descending by timestamp and take top 5
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activity = activities[:5]

        # Format timestamps to ISO strings before JSON serialization
        for act in recent_activity:
            act["timestamp"] = (
                act["timestamp"].isoformat() if act["timestamp"] else None
            )

        return jsonify(
            {
                "message": "Dashboard data fetched successfully",
                "data": {
                    "total_students": total_students,
                    "total_applications": total_applications,
                    "companies": {
                        "total": total_companies,
                        "pending": pending_companies,
                        "approved": approved_companies,
                        "rejected": rejected_companies,
                    },
                    "drives": {
                        "total": total_drives,
                        "pending": pending_drives,
                        "approved": approved_drives,
                        "rejected": rejected_drives,
                    },
                    "recent_placements": recent_placements,
                    "recent_activity": recent_activity,
                },
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies", methods=["GET"])
@admin_required
def get_companies():
    try:
        status_filter = request.args.get("status")
        search_query = request.args.get("search")

        query = db.session.query(Company, User).join(
            User, Company.user_id == User.id
        )

        if status_filter in [
            ApprovalStatus.PENDING,
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
        ]:
            query = query.filter(Company.approval_status == status_filter)

        if search_query:
            query = query.filter(
                (Company.company_name.ilike(f"%{search_query}%"))
                | (Company.industry.ilike(f"%{search_query}%"))
            )

        companies = query.all()

        result_data = []
        for company, user in companies:
            drive_count = PlacementDrive.query.filter_by(
                company_id=company.id
            ).count()
            result_data.append(
                {
                    "id": company.id,
                    "company_name": company.company_name,
                    "approval_status": company.approval_status,
                    "email": user.email,
                    "drive_count": drive_count,
                    "industry": company.industry,
                    "hr_name": company.hr_name,
                    "hr_contact": company.hr_contact,
                    "created_at": company.created_at.isoformat()
                    if company.created_at
                    else None,
                }
            )

        return jsonify(
            {"message": "Companies fetched successfully", "data": result_data}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies/<int:company_id>", methods=["GET"])
@admin_required
def get_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)

        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        drives_data = [
            {"id": d.id, "job_title": d.job_title, "status": d.status}
            for d in drives
        ]

        return jsonify(
            {
                "message": "Company fetched successfully",
                "data": {
                    "id": company.id,
                    "company_name": company.company_name,
                    "website": company.website,
                    "approval_status": company.approval_status,
                    "rejection_reason": company.rejection_reason,
                    "drives": drives_data,
                },
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies/<int:company_id>/approve", methods=["PATCH"])
@admin_required
def approve_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        if company.approval_status == ApprovalStatus.APPROVED:
            return jsonify({"error": "Company is already approved"}), 409

        company.approval_status = ApprovalStatus.APPROVED
        db.session.commit()

        return jsonify(
            {
                "message": "Company approved successfully",
                "data": {
                    "id": company.id,
                    "approval_status": company.approval_status,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies/<int:company_id>/reject", methods=["PATCH"])
@admin_required
def reject_company(company_id):
    try:
        data = request.get_json()
        if not data or "reason" not in data:
            return jsonify({"error": "Rejection reason is required"}), 400

        company = db.get_or_404(Company, company_id)
        if company.approval_status == ApprovalStatus.REJECTED:
            return jsonify({"error": "Company is already rejected"}), 409

        company.approval_status = ApprovalStatus.REJECTED
        company.rejection_reason = data["reason"]
        db.session.commit()

        return jsonify(
            {
                "message": "Company rejected successfully",
                "data": {
                    "id": company.id,
                    "approval_status": company.approval_status,
                    "rejection_reason": company.rejection_reason,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["PATCH"])
@admin_required
def blacklist_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        user = db.get_or_404(User, company.user_id)

        if user.account_status == AccountStatus.BLACKLISTED:
            return jsonify({"error": "Account is already blacklisted"}), 409

        user.account_status = AccountStatus.BLACKLISTED
        db.session.commit()

        return jsonify(
            {
                "message": "Company blacklisted successfully",
                "data": {
                    "company_id": company.id,
                    "account_status": user.account_status,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/companies/<int:company_id>/activate", methods=["PATCH"])
@admin_required
def activate_company(company_id):
    try:
        company = db.get_or_404(Company, company_id)
        user = db.get_or_404(User, company.user_id)

        if user.account_status == AccountStatus.ACTIVE:
            return jsonify({"error": "Account is already active"}), 409

        user.account_status = AccountStatus.ACTIVE
        db.session.commit()

        return jsonify(
            {
                "message": "Company account activated successfully",
                "data": {
                    "company_id": company.id,
                    "account_status": user.account_status,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    try:
        search_query = request.args.get("search")
        branch_filter = request.args.get("branch")
        is_placed_filter = request.args.get("is_placed")

        query = db.session.query(Student, User).join(
            User, Student.user_id == User.id
        )

        if search_query:
            query = query.filter(
                (Student.full_name.ilike(f"%{search_query}%"))
                | (Student.user_id.has(email=search_query))
            )

        if branch_filter:
            query = query.filter(Student.branch == branch_filter)

        if is_placed_filter is not None:
            is_placed = is_placed_filter.lower() == "true"
            query = query.filter(Student.is_placed == is_placed)

        students = query.all()

        result_data = []
        for student, user in students:
            result_data.append(
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
            )

        return jsonify(
            {"message": "Students fetched successfully", "data": result_data}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/students/<int:student_id>", methods=["GET"])
@admin_required
def get_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)

        applications = (
            Application.query.filter_by(student_id=student.id)
            .join(PlacementDrive)
            .join(Company)
            .all()
        )
        apps_data = []
        for app in applications:
            apps_data.append(
                {
                    "id": app.id,
                    "drive_title": app.drive.job_title,
                    "company_name": app.drive.company.company_name,
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat()
                    if app.applied_at
                    else None,
                }
            )

        return jsonify(
            {
                "message": "Student fetched successfully",
                "data": {
                    "id": student.id,
                    "name": student.full_name,
                    "branch": student.branch,
                    "cgpa": student.cgpa,
                    "applications": apps_data,
                },
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/students/<int:student_id>/blacklist", methods=["PATCH"])
@admin_required
def blacklist_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)
        user = db.get_or_404(User, student.user_id)

        if user.account_status == AccountStatus.BLACKLISTED:
            return jsonify({"error": "Account is already blacklisted"}), 409

        user.account_status = AccountStatus.BLACKLISTED
        db.session.commit()

        return jsonify(
            {
                "message": "Student blacklisted successfully",
                "data": {
                    "student_id": student.id,
                    "account_status": user.account_status,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/students/<int:student_id>/activate", methods=["PATCH"])
@admin_required
def activate_student(student_id):
    try:
        student = db.get_or_404(Student, student_id)
        user = db.get_or_404(User, student.user_id)

        if user.account_status == AccountStatus.ACTIVE:
            return jsonify({"error": "Account is already active"}), 409

        user.account_status = AccountStatus.ACTIVE
        db.session.commit()

        return jsonify(
            {
                "message": "Student account activated successfully",
                "data": {
                    "student_id": student.id,
                    "account_status": user.account_status,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/drives", methods=["GET"])
@admin_required
def get_drives():
    try:
        status_filter = request.args.get("status")
        search_query = request.args.get("search")

        query = db.session.query(PlacementDrive).join(Company)

        if status_filter in [
            DriveStatus.PENDING,
            DriveStatus.APPROVED,
            DriveStatus.CLOSED,
        ]:
            query = query.filter(PlacementDrive.status == status_filter)

        if search_query:
            query = query.filter(
                (PlacementDrive.job_title.ilike(f"%{search_query}%"))
                | (Company.company_name.ilike(f"%{search_query}%"))
            )

        drives = query.all()

        result_data = []
        for drive in drives:
            applicant_count = Application.query.filter_by(
                drive_id=drive.id
            ).count()
            application_deadline = drive.application_deadline.isoformat()
            result_data.append(
                {
                    "id": drive.id,
                    "job_title": drive.job_title,
                    "company_name": drive.company.company_name,
                    "status": drive.status,
                    "application_deadline": application_deadline,
                    "applicant_count": applicant_count,
                    "job_type": drive.job_type,
                    "salary_package": drive.salary_package,
                    "eligible_branches": drive.eligible_branches,
                    "min_cgpa": drive.min_cgpa,
                    "other_criteria": drive.other_criteria,
                }
            )

        return jsonify(
            {"message": "Drives fetched successfully", "data": result_data}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/drives/<int:drive_id>", methods=["GET"])
@admin_required
def get_drive(drive_id):
    try:
        drive = db.get_or_404(PlacementDrive, drive_id)

        applications = (
            Application.query.filter_by(drive_id=drive.id).join(Student).all()
        )
        apps_data = []
        for app in applications:
            apps_data.append(
                {
                    "id": app.id,
                    "student_name": app.student.full_name,
                    "student_id": app.student.id,
                    "status": app.status,
                }
            )

        return jsonify(
            {
                "message": "Drive fetched successfully",
                "data": {
                    "id": drive.id,
                    "job_title": drive.job_title,
                    "company_name": drive.company.company_name,
                    "description": drive.job_description,
                    "status": drive.status,
                    "applications": apps_data,
                },
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["PATCH"])
@admin_required
def approve_drive(drive_id):
    try:
        drive = db.get_or_404(PlacementDrive, drive_id)
        if drive.status == DriveStatus.APPROVED:
            return jsonify({"error": "Drive is already approved"}), 409

        drive.status = DriveStatus.APPROVED
        db.session.commit()

        return jsonify(
            {
                "message": "Drive approved successfully",
                "data": {"id": drive.id, "status": drive.status},
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["PATCH"])
@admin_required
def reject_drive(drive_id):
    try:
        data = request.get_json()
        if not data or "reason" not in data:
            return jsonify({"error": "Rejection reason is required"}), 400

        drive = db.get_or_404(PlacementDrive, drive_id)
        if drive.status == DriveStatus.REJECTED:
            return jsonify({"error": "Drive is already rejected"}), 409

        drive.status = DriveStatus.REJECTED
        drive.rejection_reason = data["reason"]
        db.session.commit()

        return jsonify(
            {
                "message": "Drive rejected successfully",
                "data": {
                    "id": drive.id,
                    "status": drive.status,
                    "rejection_reason": drive.rejection_reason,
                },
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/applications", methods=["GET"])
@admin_required
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

        result_data = []
        for app in applications:
            result_data.append(
                {
                    "id": app.id,
                    "student_name": app.student.full_name,
                    "student_branch": app.student.branch,
                    "student_year": app.student.year,
                    "drive_title": app.drive.job_title,
                    "company_name": app.drive.company.company_name,
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat()
                    if app.applied_at
                    else None,
                }
            )

        return jsonify(
            {
                "message": "Applications fetched successfully",
                "data": result_data,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
