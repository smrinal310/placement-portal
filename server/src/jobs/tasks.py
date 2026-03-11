import logging
import os
import time
from calendar import monthrange
from datetime import UTC, datetime, timedelta

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    ExportJobStatus,
    UserRole,
)
from src.helpers.cel_helper import (
    _build_report_html,
    _fmt_dt,
    _na,
    _prev_month,
    _query_monthly_stats,
    _resolve_path,
    _save_report_file,
    _write_csv,
)
from src.helpers.email import send_email
from src.jobs.celery_app import celery
from src.models import (
    Application,
    Company,
    ExportJob,
    Notification,
    PlacementDrive,
    Student,
    User,
    db,
)

logger = logging.getLogger(__name__)


@celery.task(bind=True)
def send_daily_interview_reminders(self):
    """Send email reminders for interviews scheduled tomorrow."""
    start = time.time()
    logger.info("Starting daily interview reminders task")

    try:
        now = datetime.now(UTC)
        tomorrow_start = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tomorrow_end = tomorrow_start.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        applications = (
            db.session.query(Application)
            .join(Student, Application.student_id == Student.id)
            .join(User, Student.user_id == User.id)
            .join(
                PlacementDrive,
                Application.drive_id == PlacementDrive.id,
            )
            .join(Company, PlacementDrive.company_id == Company.id)
            .filter(
                Application.interview_date >= tomorrow_start,
                Application.interview_date <= tomorrow_end,
                Application.status.in_(
                    [
                        ApplicationStatus.SHORTLISTED,
                        ApplicationStatus.APPLIED,
                    ]
                ),
                User.account_status == AccountStatus.ACTIVE,
            )
            .all()
        )

        template_path = _resolve_path("static", "templates", "reminder.html")
        with open(template_path, encoding="utf-8") as f:
            reminder_html = f.read()

        sent, failed = 0, 0
        for app_record in applications:
            student = app_record.student
            drive = app_record.drive
            company = drive.company

            interview_dt = (
                app_record.interview_date.strftime("%A, %d %B %Y at %I:%M %p")
                if app_record.interview_date
                else "N/A"
            )
            mode = app_record.interview_mode or "N/A"
            if mode.lower() == "online" and app_record.interview_link:
                link_html = (
                    f'<a href="{app_record.interview_link}">'
                    f"{app_record.interview_link}</a>"
                )
            else:
                link_html = "In-person"

            deadline = (
                drive.application_deadline.strftime("%A, %d %B %Y at %I:%M %p")
                if drive.application_deadline
                else "N/A"
            )

            html_body = reminder_html.format(
                student_name=student.full_name,
                company_name=company.company_name,
                job_title=drive.job_title,
                interview_dt=interview_dt,
                interview_mode=mode,
                interview_link=link_html,
                deadline=deadline,
            )

            subject = (
                f"Interview Reminder – {drive.job_title} "
                f"at {company.company_name} Tomorrow"
            )

            try:
                send_email(student.user.email, subject, html_body)
                sent += 1
            except Exception:
                failed += 1
                logger.exception(
                    "Failed reminder for application %d",
                    app_record.id,
                )

        elapsed = time.time() - start
        logger.info(
            "Daily reminders done: %d sent, %d failed (%.2fs)",
            sent,
            failed,
            elapsed,
        )
    except Exception:
        logger.exception("Daily interview reminders task failed")
        raise
    finally:
        db.session.remove()


@celery.task(bind=True)
def send_monthly_placement_report(self):
    """Generate and email the previous month's placement report."""
    start = time.time()
    logger.info("Starting monthly placement report task")

    try:
        today = datetime.now(UTC)
        year, month = _prev_month(today)
        _, last_day = monthrange(year, month)
        month_start = datetime(year, month, 1, tzinfo=UTC)
        month_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=UTC)
        month_label = month_start.strftime("%B %Y")

        stats = _query_monthly_stats(month_start, month_end)
        report_html = _build_report_html(stats, month_label)
        _save_report_file(report_html, year, month)

        # Email admin
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if admin:
            subject = f"Monthly Placement Report – {month_label}"
            send_email(admin.email, subject, report_html)

            notification = Notification(
                user_id=admin.id,
                title="Monthly Report Ready",
                message=(f"Monthly report for {month_label} is ready."),
            )
            db.session.add(notification)
            db.session.commit()

        elapsed = time.time() - start
        records = stats["total_drives"] + stats["total_applications"]
        logger.info(
            "Monthly report done: %d records processed (%.2fs)",
            records,
            elapsed,
        )
    except Exception:
        logger.exception("Monthly placement report task failed")
        raise
    finally:
        db.session.remove()


STUDENT_CSV_COLUMNS = [
    "Student ID",
    "Roll Number",
    "Full Name",
    "Company Name",
    "Drive Title",
    "Job Type",
    "Job Location",
    "Salary Package",
    "Application Status",
    "Applied At",
    "Interview Date",
    "Interview Mode",
    "Company Remarks",
]


@celery.task(bind=True)
def export_student_applications_csv(self, student_id, export_job_id):
    """Generate a CSV of all applications for a student."""
    logger.info(
        "Starting student CSV export: student=%d job=%d",
        student_id,
        export_job_id,
    )
    try:
        job = db.session.get(ExportJob, export_job_id)
        if not job:
            raise ValueError(f"ExportJob {export_job_id} not found")
        job.status = ExportJobStatus.PROCESSING
        db.session.commit()

        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        applications = (
            Application.query.filter_by(student_id=student_id)
            .join(PlacementDrive)
            .join(Company)
            .all()
        )

        exports_dir = _resolve_path("static", "uploads", "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"student_{student_id}_{export_job_id}.csv"
        filepath = os.path.join(exports_dir, filename)

        rows = []
        for app_rec in applications:
            drive = app_rec.drive
            company = drive.company
            user = student.user
            rows.append(
                [
                    student.id,
                    _na(user.email.split("@")[0]),
                    student.full_name,
                    company.company_name,
                    drive.job_title,
                    _na(drive.job_type),
                    _na(drive.job_location),
                    _na(drive.salary_package),
                    app_rec.status,
                    _fmt_dt(app_rec.applied_at),
                    _fmt_dt(app_rec.interview_date),
                    _na(app_rec.interview_mode),
                    _na(app_rec.company_remarks),
                ]
            )

        _write_csv(filepath, STUDENT_CSV_COLUMNS, rows)

        job.status = ExportJobStatus.DONE
        job.file_path = filename
        job.completed_at = datetime.now(UTC)
        db.session.commit()

        notification = Notification(
            user_id=student.user_id,
            title="Export Ready",
            message=("Your application history CSV is ready for download."),
        )
        db.session.add(notification)
        db.session.commit()

        logger.info(
            "Student CSV export done: %s (%d rows)",
            filepath,
            len(applications),
        )
    except Exception:
        logger.exception(
            "Student CSV export failed: job=%d",
            export_job_id,
        )
        try:
            job = db.session.get(ExportJob, export_job_id)
            if job:
                job.status = ExportJobStatus.FAILED
                db.session.commit()

                student = db.session.get(Student, student_id)
                if student:
                    notification = Notification(
                        user_id=student.user_id,
                        title="Export Failed",
                        message=("Your export failed. Please try again."),
                    )
                    db.session.add(notification)
                    db.session.commit()
        except Exception:
            logger.exception("Failed to update ExportJob status on error")
        raise
    finally:
        db.session.remove()
