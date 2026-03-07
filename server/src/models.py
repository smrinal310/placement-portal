from datetime import UTC, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from src.constants import (
    AccountStatus,
    ApplicationStatus,
    ApprovalStatus,
    DriveStatus,
    UserRole,
)

db = SQLAlchemy()


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    account_status = db.Column(
        db.String(20), nullable=False, default=AccountStatus.ACTIVE
    )

    student_profile = db.relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company_profile = db.relationship(
        "Company",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_company(self):
        return self.role == UserRole.COMPANY

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def is_active_account(self):
        return self.account_status == AccountStatus.ACTIVE

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"


class Student(TimestampMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    full_name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)

    resume_filename = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    skills = db.Column(db.Text)

    is_placed = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship(
        "Application", back_populates="student", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student id={self.id}, name={self.full_name}>"


class Company(TimestampMixin, db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    company_name = db.Column(db.String(200), nullable=False)
    hr_name = db.Column(db.String(150))
    hr_contact = db.Column(db.String(150))
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    logo_filename = db.Column(db.String(255))
    address = db.Column(db.Text)

    approval_status = db.Column(
        db.String(20), nullable=False, default=ApprovalStatus.PENDING
    )
    rejection_reason = db.Column(db.Text)

    user = db.relationship("User", back_populates="company_profile")
    drives = db.relationship(
        "PlacementDrive",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Company id={self.id} name={self.company_name} "
            f"status={self.approval_status}>"
        )


class PlacementDrive(TimestampMixin, db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer, db.ForeignKey("companies.id"), nullable=False
    )

    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_location = db.Column(db.String(200))
    job_type = db.Column(db.String(50))
    salary_package = db.Column(db.String(100))

    eligible_branches = db.Column(db.Text)
    min_cgpa = db.Column(db.Float, default=0.0)
    max_year = db.Column(db.Integer)
    min_year = db.Column(db.Integer, default=1)
    other_criteria = db.Column(db.Text)

    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime)
    result_date = db.Column(db.DateTime)

    status = db.Column(
        db.String(20), nullable=False, default=DriveStatus.PENDING
    )
    rejection_reason = db.Column(db.Text)
    vacancy_count = db.Column(db.Integer, default=0)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship(
        "Application", back_populates="drive", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<PlacementDrive id={self.id} title={self.job_title} "
            f"company_id={self.company_id} status={self.status}>"
        )


class Application(TimestampMixin, db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id"), nullable=False
    )
    drive_id = db.Column(
        db.Integer, db.ForeignKey("placement_drives.id"), nullable=False
    )

    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    status = db.Column(
        db.String(20), nullable=False, default=ApplicationStatus.APPLIED
    )

    interview_date = db.Column(db.DateTime)
    interview_mode = db.Column(db.String(50))
    interview_link = db.Column(db.String(255))

    company_remarks = db.Column(db.Text)
    offer_letter_url = db.Column(db.String(255))

    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),
    )

    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")

    def __repr__(self):
        return (
            f"<Application id={self.id} student_id={self.student_id} "
            f"drive_id={self.drive_id} status={self.status}>"
        )
