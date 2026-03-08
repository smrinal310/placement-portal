import csv
import os
from datetime import UTC, datetime

from flask import current_app

from src.constants import ApplicationStatus, DriveStatus
from src.models import Application, Company, PlacementDrive, Student, db


def _fmt_dt(dt: datetime | None) -> str:
    """Format a datetime as 'DD MMM YYYY HH:MM' or 'N/A'."""
    if dt is None:
        return "N/A"
    return dt.strftime("%d %b %Y %H:%M")


def _na(val: str | None) -> str:
    """Return val or 'N/A' for None/empty."""
    return val if val else "N/A"


def _write_csv(
    filepath: str,
    headers: list[str],
    rows: list[list],
) -> None:
    """Write headers + rows to a CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def _resolve_path(*parts: str) -> str:
    """Build an absolute path relative to the Flask app root."""
    return os.path.join(current_app.root_path, "..", *parts)


def _prev_month(
    today: datetime,
) -> tuple[int, int]:
    """Return (year, month) of the previous calendar month."""
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def _query_monthly_stats(
    month_start: datetime,
    month_end: datetime,
) -> dict:
    """Query all statistics for the monthly report."""
    # Drives
    drives_q = PlacementDrive.query.filter(
        PlacementDrive.created_at >= month_start,
        PlacementDrive.created_at <= month_end,
    )

    # Applications
    apps_q = Application.query.filter(
        Application.applied_at >= month_start,
        Application.applied_at <= month_end,
    )

    status_counts = {}
    for s in [
        ApplicationStatus.APPLIED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
    ]:
        status_counts[s] = apps_q.filter_by(status=s).count()

    unique_students = (
        db.session.query(
            db.func.count(db.func.distinct(Application.student_id))
        )
        .filter(
            Application.applied_at >= month_start,
            Application.applied_at <= month_end,
        )
        .scalar()
    )

    students_placed = (
        db.session.query(
            db.func.count(db.func.distinct(Application.student_id))
        )
        .filter(
            Application.applied_at >= month_start,
            Application.applied_at <= month_end,
            Application.status == ApplicationStatus.SELECTED,
        )
        .scalar()
    )

    top_companies = (
        db.session.query(
            Company.company_name,
            db.func.count(Application.id).label("cnt"),
        )
        .join(
            PlacementDrive,
            PlacementDrive.company_id == Company.id,
        )
        .join(
            Application,
            Application.drive_id == PlacementDrive.id,
        )
        .filter(
            Application.applied_at >= month_start,
            Application.applied_at <= month_end,
            Application.status == ApplicationStatus.SELECTED,
        )
        .group_by(Company.id)
        .order_by(db.func.count(Application.id).desc())
        .limit(5)
        .all()
    )

    top_drives = (
        db.session.query(
            PlacementDrive.job_title,
            Company.company_name,
            db.func.count(Application.id).label("cnt"),
        )
        .join(
            Application,
            Application.drive_id == PlacementDrive.id,
        )
        .join(
            Company,
            PlacementDrive.company_id == Company.id,
        )
        .filter(
            Application.applied_at >= month_start,
            Application.applied_at <= month_end,
        )
        .group_by(PlacementDrive.id)
        .order_by(db.func.count(Application.id).desc())
        .limit(5)
        .all()
    )

    branch_breakdown = (
        db.session.query(
            Student.branch,
            db.func.count(Application.id).label("cnt"),
        )
        .join(Application, Application.student_id == Student.id)
        .filter(
            Application.applied_at >= month_start,
            Application.applied_at <= month_end,
            Application.status == ApplicationStatus.SELECTED,
        )
        .group_by(Student.branch)
        .order_by(db.func.count(Application.id).desc())
        .all()
    )

    return {
        "total_drives": drives_q.count(),
        "approved_drives": drives_q.filter_by(
            status=DriveStatus.APPROVED
        ).count(),
        "rejected_drives": drives_q.filter_by(
            status=DriveStatus.REJECTED
        ).count(),
        "pending_drives": drives_q.filter_by(
            status=DriveStatus.PENDING
        ).count(),
        "total_applications": apps_q.count(),
        "unique_students": unique_students or 0,
        "students_placed": students_placed or 0,
        "status_counts": status_counts,
        "top_companies": top_companies,
        "top_drives": top_drives,
        "branch_breakdown": branch_breakdown,
    }


def _build_report_html(stats: dict, month_label: str) -> str:
    """Build the HTML report from stats dict."""
    row_tpl = (
        '<tr><td style="padding:8px;border:1px solid #ddd;">'
        "{col1}</td>"
        '<td style="padding:8px;border:1px solid #ddd;'
        'text-align:right;">{col2}</td></tr>'
    )
    row3_tpl = (
        '<tr><td style="padding:8px;border:1px solid #ddd;">'
        "{col1}</td>"
        '<td style="padding:8px;border:1px solid #ddd;">'
        "{col2}</td>"
        '<td style="padding:8px;border:1px solid #ddd;'
        'text-align:right;">{col3}</td></tr>'
    )

    status_rows = "".join(
        row_tpl.format(col1=s.capitalize(), col2=c)
        for s, c in stats["status_counts"].items()
    )
    top_companies_rows = "".join(
        row_tpl.format(col1=name, col2=cnt)
        for name, cnt in stats["top_companies"]
    )
    top_drives_rows = "".join(
        row3_tpl.format(col1=title, col2=comp, col3=cnt)
        for title, comp, cnt in stats["top_drives"]
    )
    branch_rows = "".join(
        row_tpl.format(col1=branch, col2=cnt)
        for branch, cnt in stats["branch_breakdown"]
    )

    template_path = _resolve_path("static", "templates", "report.html")
    with open(template_path, encoding="utf-8") as f:
        report_html = f.read()

    return report_html.format(
        month_year=month_label,
        total_drives=stats["total_drives"],
        approved_drives=stats["approved_drives"],
        rejected_drives=stats["rejected_drives"],
        pending_drives=stats["pending_drives"],
        total_applications=stats["total_applications"],
        unique_students=stats["unique_students"],
        students_placed=stats["students_placed"],
        status_rows=status_rows or row_tpl.format(col1="—", col2="0"),
        top_companies_rows=top_companies_rows
        or row_tpl.format(col1="No data", col2="—"),
        top_drives_rows=top_drives_rows
        or row3_tpl.format(col1="No data", col2="—", col3="—"),
        branch_rows=branch_rows or row_tpl.format(col1="No data", col2="—"),
        generated_at=datetime.now(UTC).strftime("%d %B %Y at %I:%M %p UTC"),
    )


def _save_report_file(html: str, year: int, month: int) -> str:
    """Save the HTML report file and return the filepath."""
    reports_dir = _resolve_path("static", "uploads", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"report_{year}_{month:02d}.html"
    filepath = os.path.join(reports_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath
