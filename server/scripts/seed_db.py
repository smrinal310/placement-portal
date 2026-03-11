"""
Seed script — populates the database with ~150+ dummy records.

Approximate counts:
  12 companies  (+ 12 user accounts)
  30 placement drives
  50 students   (+ 50 user accounts)
  ~100-130 applications  (generated based on branch / CGPA eligibility)

Usage (from the server/ directory):
    python scripts/seed_db.py

Pass --reset to drop all company/student/drive/application rows first:
    python scripts/seed_db.py --reset

The script is idempotent without --reset: emails already in the users table
are skipped.
"""

import argparse
import os
import random
import sys
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.exc import IntegrityError

# Allow importing the Flask app from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import create_app
from src.constants import (
    ApplicationStatus,
    ApprovalStatus,
    DriveStatus,
    UserRole,
)
from src.models import Application, Company, PlacementDrive, Student, User, db

random.seed(42)

# ── Companies (12) ────────────────────────────────────────────────────────────

COMPANIES = [
    {
        "email": "hr@techcorp.io",
        "password": "Password@123",
        "company_name": "TechCorp Solutions",
        "hr_name": "Sarah Williams",
        "hr_contact": "hr@techcorp.io",
        "website": "https://www.techcorp.io",
        "industry": "Technology",
        "description": (
            "TechCorp Solutions is a global leader in enterprise-grade software "
            "infrastructure and digital transformation. Founded in 2008, we have "
            "consistently pushed the boundaries of cloud computing, cybersecurity, "
            "and AI-driven automation.\n\n"
            "Our mission is to empower organizations with tools to thrive in an "
            "increasingly digital world."
        ),
        "address": "123 Tech Plaza, Suite 400, San Francisco, CA 94105",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "careers@globalfinance.com",
        "password": "Password@123",
        "company_name": "Global Finance Group",
        "hr_name": "Michael Chen",
        "hr_contact": "careers@globalfinance.com",
        "website": "https://www.globalfinance.com",
        "industry": "Finance",
        "description": (
            "Global Finance Group is one of the largest investment banking and "
            "financial services firms, operating across 40+ countries with a focus "
            "on M&A advisory, equity capital markets, and quantitative research."
        ),
        "address": "One Financial Centre, New York, NY 10004",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "recruit@innovateai.com",
        "password": "Password@123",
        "company_name": "InnovateAI Labs",
        "hr_name": "Priya Sharma",
        "hr_contact": "recruit@innovateai.com",
        "website": "https://www.innovateai.com",
        "industry": "Artificial Intelligence",
        "description": (
            "InnovateAI Labs builds next-generation ML platforms used by Fortune 500 "
            "companies. We hire top talent in ML engineering, data science, and AI "
            "research, with a fast-paced culture and meaningful work from day one."
        ),
        "address": "88 Innovation Drive, Palo Alto, CA 94304",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "jobs@infrabuilders.in",
        "password": "Password@123",
        "company_name": "Infra Builders Ltd",
        "hr_name": "Ramesh Anand",
        "hr_contact": "jobs@infrabuilders.in",
        "website": "https://www.infrabuilders.in",
        "industry": "Civil Engineering",
        "description": (
            "Infra Builders Ltd is a leading infrastructure and construction company "
            "with projects spanning highways, bridges, and smart city developments "
            "across India. We operate on a philosophy of precision, safety, and "
            "sustainability."
        ),
        "address": "Plot 14, MIDC Industrial Area, Pune 411019",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "hr@greenpower.org",
        "password": "Password@123",
        "company_name": "GreenPower Energy",
        "hr_name": "Anita Desai",
        "hr_contact": "hr@greenpower.org",
        "website": "https://www.greenpower.org",
        "industry": "Renewable Energy",
        "description": (
            "GreenPower Energy develops and operates solar, wind, and hydrogen energy "
            "plants. We are on a mission to make clean energy accessible and affordable "
            "through scalable engineering and smart grid technology."
        ),
        "address": "Tower B, Eco Park, Hyderabad 500032",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "talent@meditech.health",
        "password": "Password@123",
        "company_name": "MediTech Systems",
        "hr_name": "Dr. Reena Kapoor",
        "hr_contact": "talent@meditech.health",
        "website": "https://www.meditech.health",
        "industry": "Healthcare Technology",
        "description": (
            "MediTech Systems provides AI-driven diagnostic tools and hospital "
            "management software to 500+ healthcare institutions. We blend medicine "
            "with software engineering to improve patient outcomes at scale."
        ),
        "address": "45 Wellness Hub, Bengaluru 560100",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "hr@cloudnine.net",
        "password": "Password@123",
        "company_name": "CloudNine Networks",
        "hr_name": "Arjun Pillai",
        "hr_contact": "hr@cloudnine.net",
        "website": "https://www.cloudnine.net",
        "industry": "Cloud Computing",
        "description": (
            "CloudNine Networks is a managed cloud services provider offering "
            "infrastructure-as-a-service, private cloud deployments, and 24/7 NOC "
            "operations for mid-market and enterprise customers globally."
        ),
        "address": "Silicon Tower, Whitefield, Bengaluru 560066",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "campus@autodrive.co",
        "password": "Password@123",
        "company_name": "AutoDrive Corp",
        "hr_name": "Suresh Iyer",
        "hr_contact": "campus@autodrive.co",
        "website": "https://www.autodrive.co",
        "industry": "Automotive",
        "description": (
            "AutoDrive Corp is at the forefront of autonomous vehicle technology, "
            "developing ADAS systems, EV powertrains, and embedded control units "
            "deployed in vehicles across three continents."
        ),
        "address": "Industrial Park, Manesar, Gurugram 122050",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "hr@datastream.io",
        "password": "Password@123",
        "company_name": "DataStream Analytics",
        "hr_name": "Kavitha Nair",
        "hr_contact": "hr@datastream.io",
        "website": "https://www.datastream.io",
        "industry": "Data Analytics",
        "description": (
            "DataStream Analytics helps businesses turn raw data into actionable "
            "intelligence through real-time streaming pipelines, BI dashboards, and "
            "predictive analytics services."
        ),
        "address": "Level 12, Cybercity, Hyderabad 500081",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "recruit@cybershield.io",
        "password": "Password@123",
        "company_name": "CyberShield Security",
        "hr_name": "Vikram Bose",
        "hr_contact": "recruit@cybershield.io",
        "website": "https://www.cybershield.io",
        "industry": "Cybersecurity",
        "description": (
            "CyberShield Security provides offensive and defensive cybersecurity "
            "services to global enterprises, including penetration testing, red team "
            "operations, SIEM deployment, and SOC-as-a-service."
        ),
        "address": "Cyber Hub, DLF Phase 2, Gurugram 122002",
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "email": "jobs@quantumsoft.dev",
        "password": "Password@123",
        "company_name": "QuantumSoft Labs",
        "hr_name": "Aditya Menon",
        "hr_contact": "jobs@quantumsoft.dev",
        "website": "https://www.quantumsoft.dev",
        "industry": "Software Products",
        "description": (
            "QuantumSoft Labs builds developer tools and SaaS products used by over "
            "200,000 engineers worldwide. Our flagship product is a collaborative "
            "low-code platform for API orchestration and workflow automation."
        ),
        "address": "3rd Floor, NASSCOM Hub, Pune 411057",
        "approval_status": ApprovalStatus.PENDING,
    },
    {
        "email": "hr@biogenesis.pharma",
        "password": "Password@123",
        "company_name": "BioGenesis Pharma",
        "hr_name": "Dr. Leena Trivedi",
        "hr_contact": "hr@biogenesis.pharma",
        "website": "https://www.biogenesis.pharma",
        "industry": "Pharmaceuticals",
        "description": (
            "BioGenesis Pharma is a research-driven pharmaceutical company focused "
            "on developing novel therapies for oncology and rare diseases. We leverage "
            "bioinformatics and computational chemistry in our drug discovery pipeline."
        ),
        "address": "BioTech Park, Genome Valley, Hyderabad 500078",
        "approval_status": ApprovalStatus.PENDING,
    },
]

# ── Drives (30) ───────────────────────────────────────────────────────────────
# company_index refers to position in COMPANIES list above.

DRIVES = [
    # ── TechCorp Solutions [0] — 3 drives ────────────────────────────────────
    {
        "company_index": 0,
        "job_title": "Software Engineer – Campus 2025",
        "job_description": (
            "Design and build scalable backend services using Python and Go. "
            "Work closely with product and infrastructure teams to ship features "
            "used by millions of enterprise customers."
        ),
        "job_location": "San Francisco, CA (Hybrid)",
        "job_type": "Full-time",
        "salary_package": "₹18 – 24 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 15,
        "other_criteria": "1. Online Assessment\n2. Technical Interview (DSA)\n3. System Design Round\n4. HR Round",
        "deadline_offset": 30,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 0,
        "job_title": "Product Management Intern – Summer 2025",
        "job_description": (
            "Work alongside senior PMs to define product roadmaps, conduct user "
            "research, and collaborate with engineering teams on feature delivery."
        ),
        "job_location": "San Francisco, CA (On-site)",
        "job_type": "Internship",
        "salary_package": "₹80K / month",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.5,
        "max_year": 2026,
        "vacancy_count": 5,
        "other_criteria": "1. Case Study Round\n2. PM Interview\n3. HR Round",
        "deadline_offset": 15,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 0,
        "job_title": "DevOps Engineer",
        "job_description": (
            "Build and maintain CI/CD pipelines, manage Kubernetes clusters, and "
            "collaborate with developers to improve deployment reliability and speed."
        ),
        "job_location": "Remote",
        "job_type": "Full-time",
        "salary_package": "₹16 – 22 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 8,
        "other_criteria": "1. Technical Screening\n2. DevOps Practical\n3. System Design\n4. HR",
        "deadline_offset": 22,
        "status": DriveStatus.APPROVED,
    },
    # ── Global Finance Group [1] — 3 drives ──────────────────────────────────
    {
        "company_index": 1,
        "job_title": "Quantitative Analyst – Graduate Programme",
        "job_description": (
            "Develop and maintain quantitative models for pricing derivatives, risk "
            "calculation, and portfolio optimisation. Strong mathematical background "
            "required."
        ),
        "job_location": "New York, NY",
        "job_type": "Full-time",
        "salary_package": "₹32 – 45 LPA",
        "eligible_branches": "Computer Science, Electronics, Electrical",
        "min_cgpa": 8.0,
        "max_year": 2025,
        "vacancy_count": 8,
        "other_criteria": "1. Aptitude Test\n2. Technical Round (Statistics)\n3. Final Interview",
        "deadline_offset": -5,
        "status": DriveStatus.CLOSED,
    },
    {
        "company_index": 1,
        "job_title": "Investment Banking Analyst",
        "job_description": (
            "Support deal execution across M&A, ECM, and DCM transactions. Produce "
            "financial models, pitch books, and client presentations."
        ),
        "job_location": "Mumbai, India",
        "job_type": "Full-time",
        "salary_package": "₹22 – 30 LPA",
        "eligible_branches": "Computer Science, Mechanical, Civil",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Written Test\n2. Group Discussion\n3. Panel Interview",
        "deadline_offset": 45,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 1,
        "job_title": "Risk Management Associate",
        "job_description": (
            "Identify, assess, and mitigate operational and financial risk across "
            "trading desks. Build risk frameworks with VP-level stakeholders."
        ),
        "job_location": "London, UK",
        "job_type": "Full-time",
        "salary_package": "₹28 – 38 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 6,
        "other_criteria": "1. Numerical Reasoning Test\n2. Case Interview\n3. Panel Discussion",
        "deadline_offset": 35,
        "status": DriveStatus.APPROVED,
    },
    # ── InnovateAI Labs [2] — 3 drives ────────────────────────────────────────
    {
        "company_index": 2,
        "job_title": "ML Engineer",
        "job_description": (
            "Build, train, and deploy large-scale ML models. Work on NLP, computer "
            "vision, and recommendation systems deployed in production at scale."
        ),
        "job_location": "Palo Alto, CA (Remote-friendly)",
        "job_type": "Full-time",
        "salary_package": "₹28 – 40 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 12,
        "other_criteria": "1. Coding Assessment\n2. ML Concepts Interview\n3. System Design\n4. Culture Fit",
        "deadline_offset": 20,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 2,
        "job_title": "Data Science Intern",
        "job_description": (
            "Assist the research team in analysing large datasets, building predictive "
            "models, and presenting insights to stakeholders."
        ),
        "job_location": "Remote",
        "job_type": "Internship",
        "salary_package": "₹60K / month",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.0,
        "max_year": 2026,
        "vacancy_count": 6,
        "other_criteria": "1. Take-home Assignment\n2. Technical Interview",
        "deadline_offset": 10,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 2,
        "job_title": "AI Research Scientist",
        "job_description": (
            "Conduct original research in reinforcement learning, transformer "
            "architectures, and agentic AI. Publish findings and prototype novel "
            "solutions."
        ),
        "job_location": "Palo Alto, CA",
        "job_type": "Full-time",
        "salary_package": "₹40 – 60 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 8.5,
        "max_year": 2025,
        "vacancy_count": 4,
        "other_criteria": "1. Research Portfolio Review\n2. Technical Deep Dive\n3. Final Panel",
        "deadline_offset": 18,
        "status": DriveStatus.PENDING,
    },
    # ── Infra Builders Ltd [3] — 3 drives ────────────────────────────────────
    {
        "company_index": 3,
        "job_title": "Civil Site Engineer",
        "job_description": (
            "Manage day-to-day site activities, supervise contractors, and ensure "
            "adherence to project timelines and safety standards."
        ),
        "job_location": "Pune, India",
        "job_type": "Full-time",
        "salary_package": "₹6 – 9 LPA",
        "eligible_branches": "Civil",
        "min_cgpa": 6.0,
        "max_year": 2025,
        "vacancy_count": 20,
        "other_criteria": "1. Technical Test\n2. Site Interview",
        "deadline_offset": 25,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 3,
        "job_title": "Structural Design Engineer",
        "job_description": (
            "Prepare structural drawings and calculations for residential and "
            "commercial projects using AutoCAD and STAAD Pro."
        ),
        "job_location": "Mumbai, India",
        "job_type": "Full-time",
        "salary_package": "₹7 – 11 LPA",
        "eligible_branches": "Civil, Mechanical",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Design Test\n2. Technical Interview\n3. HR",
        "deadline_offset": 40,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 3,
        "job_title": "Project Planning Engineer",
        "job_description": (
            "Develop project schedules using Primavera and MS Project, track "
            "milestones, and coordinate between design and site teams."
        ),
        "job_location": "Delhi NCR",
        "job_type": "Full-time",
        "salary_package": "₹8 – 12 LPA",
        "eligible_branches": "Civil, Mechanical",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 5,
        "other_criteria": "1. Planning Software Test\n2. HR Interview",
        "deadline_offset": 50,
        "status": DriveStatus.PENDING,
    },
    # ── GreenPower Energy [4] — 2 drives ─────────────────────────────────────
    {
        "company_index": 4,
        "job_title": "Solar Systems Engineer",
        "job_description": (
            "Design and commission utility-scale solar PV plants. Perform energy "
            "yield assessments and manage EPC contractors."
        ),
        "job_location": "Hyderabad, India",
        "job_type": "Full-time",
        "salary_package": "₹8 – 13 LPA",
        "eligible_branches": "Electrical, Electronics, Mechanical",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 12,
        "other_criteria": "1. Technical Test\n2. Design Interview\n3. HR",
        "deadline_offset": 28,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 4,
        "job_title": "Energy Data Analyst",
        "job_description": (
            "Analyse operational data from wind and solar farms to identify "
            "performance bottlenecks and recommend efficiency improvements."
        ),
        "job_location": "Remote",
        "job_type": "Full-time",
        "salary_package": "₹7 – 10 LPA",
        "eligible_branches": "Electrical, Computer Science, Information Technology",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 8,
        "other_criteria": "1. Data Analysis Assignment\n2. Technical Interview",
        "deadline_offset": 32,
        "status": DriveStatus.APPROVED,
    },
    # ── MediTech Systems [5] — 2 drives ──────────────────────────────────────
    {
        "company_index": 5,
        "job_title": "Healthcare Software Developer",
        "job_description": (
            "Build HL7/FHIR-compliant APIs and patient-facing web applications. "
            "Work with cross-functional teams including doctors and data scientists."
        ),
        "job_location": "Bengaluru, India",
        "job_type": "Full-time",
        "salary_package": "₹12 – 18 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Coding Round\n2. System Design\n3. Culture Interview",
        "deadline_offset": 25,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 5,
        "job_title": "Clinical Data Analyst",
        "job_description": (
            "Process and analyse clinical trial data using Python and R. Build "
            "statistical models to support regulatory submissions."
        ),
        "job_location": "Bengaluru, India",
        "job_type": "Full-time",
        "salary_package": "₹9 – 14 LPA",
        "eligible_branches": "Computer Science, Information Technology, Chemical",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 6,
        "other_criteria": "1. Statistics Test\n2. Python/R Coding Interview\n3. HR",
        "deadline_offset": 30,
        "status": DriveStatus.APPROVED,
    },
    # ── CloudNine Networks [6] — 3 drives ────────────────────────────────────
    {
        "company_index": 6,
        "job_title": "Network Engineer",
        "job_description": (
            "Design, deploy, and troubleshoot enterprise network infrastructure "
            "including routing, switching, and SD-WAN solutions."
        ),
        "job_location": "Bengaluru, India",
        "job_type": "Full-time",
        "salary_package": "₹8 – 14 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 15,
        "other_criteria": "1. Networking MCQ\n2. Lab Practical\n3. HR",
        "deadline_offset": 20,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 6,
        "job_title": "Cloud Solutions Architect",
        "job_description": (
            "Architect multi-cloud environments on AWS, GCP, and Azure for enterprise "
            "clients. Lead migration and modernisation projects end-to-end."
        ),
        "job_location": "Remote",
        "job_type": "Full-time",
        "salary_package": "₹20 – 30 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 7,
        "other_criteria": "1. Cloud Technical Test\n2. Architecture Review\n3. Panel Interview",
        "deadline_offset": 35,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 6,
        "job_title": "Systems Administrator",
        "job_description": (
            "Maintain Linux/Windows server infrastructure, manage virtualisation "
            "(VMware/KVM), and handle incident escalations for enterprise clients."
        ),
        "job_location": "Bengaluru, India",
        "job_type": "Full-time",
        "salary_package": "₹6 – 10 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 6.0,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Technical MCQ\n2. Practical Hands-on\n3. HR",
        "deadline_offset": 15,
        "status": DriveStatus.PENDING,
    },
    # ── AutoDrive Corp [7] — 2 drives ─────────────────────────────────────────
    {
        "company_index": 7,
        "job_title": "Embedded Systems Engineer",
        "job_description": (
            "Develop firmware for ADAS ECUs using C/C++ and AUTOSAR. Write BSP "
            "drivers, validate hardware, and support HIL testing."
        ),
        "job_location": "Gurugram, India",
        "job_type": "Full-time",
        "salary_package": "₹10 – 16 LPA",
        "eligible_branches": "Electronics, Electrical, Computer Science",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 15,
        "other_criteria": "1. C/C++ Coding Test\n2. Embedded Systems Interview\n3. HR",
        "deadline_offset": 30,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 7,
        "job_title": "Automotive Software Engineer",
        "job_description": (
            "Develop and test software for electric vehicle powertrain control systems. "
            "Experience with CAN/LIN bus and model-based development preferred."
        ),
        "job_location": "Chennai, India",
        "job_type": "Full-time",
        "salary_package": "₹12 – 18 LPA",
        "eligible_branches": "Mechanical, Electronics, Electrical",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Technical Screening\n2. Domain Interview\n3. Final Round",
        "deadline_offset": 25,
        "status": DriveStatus.APPROVED,
    },
    # ── DataStream Analytics [8] — 2 drives ──────────────────────────────────
    {
        "company_index": 8,
        "job_title": "Business Intelligence Analyst",
        "job_description": (
            "Build interactive Tableau and Power BI dashboards for C-suite "
            "stakeholders. Design star-schema data models and write complex SQL queries."
        ),
        "job_location": "Hyderabad, India",
        "job_type": "Full-time",
        "salary_package": "₹9 – 14 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 12,
        "other_criteria": "1. SQL Test\n2. BI Tool Demo\n3. HR",
        "deadline_offset": 20,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 8,
        "job_title": "Data Engineer",
        "job_description": (
            "Architect and operate real-time data pipelines using Apache Kafka, "
            "Spark, and Flink. Build and maintain data lakes on AWS S3 and GCS."
        ),
        "job_location": "Hyderabad, India",
        "job_type": "Full-time",
        "salary_package": "₹14 – 22 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 8,
        "other_criteria": "1. Coding Round\n2. Data Engineering Design Interview\n3. HR",
        "deadline_offset": 28,
        "status": DriveStatus.APPROVED,
    },
    # ── CyberShield Security [9] — 2 drives ──────────────────────────────────
    {
        "company_index": 9,
        "job_title": "Security Analyst",
        "job_description": (
            "Monitor SIEM dashboards, investigate security incidents, and develop "
            "detection rules. Collaborate with the blue team on threat hunting."
        ),
        "job_location": "Gurugram, India",
        "job_type": "Full-time",
        "salary_package": "₹10 – 16 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Security MCQ\n2. Incident Response Simulation\n3. HR",
        "deadline_offset": 22,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 9,
        "job_title": "Penetration Tester",
        "job_description": (
            "Conduct web, mobile, and network penetration tests for enterprise clients. "
            "Write detailed reports and provide remediation guidance."
        ),
        "job_location": "Remote",
        "job_type": "Full-time",
        "salary_package": "₹12 – 20 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 6,
        "other_criteria": "1. CTF Challenge\n2. Pentest Methodology Interview\n3. Technical Panel",
        "deadline_offset": 18,
        "status": DriveStatus.APPROVED,
    },
    {
        "company_index": 9,
        "job_title": "Cloud Security Engineer",
        "job_description": (
            "Secure cloud-native workloads on AWS and Azure. Design IAM policies, "
            "implement container security, and perform cloud configuration audits."
        ),
        "job_location": "Gurugram, India (Hybrid)",
        "job_type": "Full-time",
        "salary_package": "₹14 – 22 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 5,
        "other_criteria": "1. Cloud Security Assessment\n2. Technical Interview\n3. HR",
        "deadline_offset": 25,
        "status": DriveStatus.APPROVED,
    },
    # ── QuantumSoft Labs [10] — 2 drives ──────────────────────────────────────
    {
        "company_index": 10,
        "job_title": "Full Stack Developer",
        "job_description": (
            "Build and ship features across the stack using React, Node.js, and "
            "PostgreSQL. Own complete feature delivery from design to deployment."
        ),
        "job_location": "Pune, India",
        "job_type": "Full-time",
        "salary_package": "₹12 – 18 LPA",
        "eligible_branches": "Computer Science, Information Technology",
        "min_cgpa": 6.5,
        "max_year": 2026,
        "vacancy_count": 20,
        "other_criteria": "1. Coding Assessment\n2. Technical Interview\n3. HR",
        "deadline_offset": 40,
        "status": DriveStatus.PENDING,
    },
    {
        "company_index": 10,
        "job_title": "Backend Engineer",
        "job_description": (
            "Design and scale microservices using Go and Kubernetes. Own service "
            "reliability, API contracts, and database performance."
        ),
        "job_location": "Pune, India (Hybrid)",
        "job_type": "Full-time",
        "salary_package": "₹14 – 22 LPA",
        "eligible_branches": "Computer Science, Information Technology, Electronics",
        "min_cgpa": 7.0,
        "max_year": 2025,
        "vacancy_count": 10,
        "other_criteria": "1. Algorithmic Round\n2. System Design\n3. HR",
        "deadline_offset": 45,
        "status": DriveStatus.PENDING,
    },
    # ── BioGenesis Pharma [11] — 2 drives ────────────────────────────────────
    {
        "company_index": 11,
        "job_title": "Bioinformatics Engineer",
        "job_description": (
            "Develop computational pipelines for genomic data analysis using Python, "
            "R, and cloud HPC clusters to process large-scale sequencing data."
        ),
        "job_location": "Hyderabad, India",
        "job_type": "Full-time",
        "salary_package": "₹10 – 16 LPA",
        "eligible_branches": "Computer Science, Information Technology, Chemical",
        "min_cgpa": 7.5,
        "max_year": 2025,
        "vacancy_count": 8,
        "other_criteria": "1. Bioinformatics Assessment\n2. Coding Interview\n3. HR",
        "deadline_offset": 35,
        "status": DriveStatus.PENDING,
    },
    {
        "company_index": 11,
        "job_title": "Chemical Process Engineer",
        "job_description": (
            "Optimise pharmaceutical manufacturing processes using lean methodologies, "
            "design of experiments, and process simulation tools."
        ),
        "job_location": "Hyderabad, India",
        "job_type": "Full-time",
        "salary_package": "₹8 – 13 LPA",
        "eligible_branches": "Chemical, Mechanical",
        "min_cgpa": 6.5,
        "max_year": 2025,
        "vacancy_count": 6,
        "other_criteria": "1. Process Engineering Test\n2. Plant Visit Interview",
        "deadline_offset": 40,
        "status": DriveStatus.PENDING,
    },
]

# ── Student generation (50 students) ─────────────────────────────────────────

_FIRST_NAMES = [
    "Aarav",
    "Priya",
    "Rohan",
    "Sneha",
    "Vikram",
    "Ananya",
    "Harsh",
    "Kavya",
    "Arjun",
    "Divya",
    "Rahul",
    "Nisha",
    "Karan",
    "Aisha",
    "Aditya",
    "Simran",
    "Nikhil",
    "Anjali",
    "Siddharth",
    "Meera",
    "Ravi",
    "Tanya",
    "Amit",
    "Ritika",
    "Yash",
    "Sakshi",
    "Vivek",
    "Deepika",
    "Aakash",
    "Rohini",
    "Ishaan",
    "Shruti",
    "Gaurav",
    "Neha",
    "Varun",
    "Pallavi",
    "Kunal",
    "Swati",
    "Dhruv",
    "Monica",
    "Parth",
    "Lakshmi",
    "Suresh",
    "Tanvi",
    "Abhinav",
    "Rekha",
    "Jayant",
    "Sunita",
    "Chetan",
    "Bhavna",
]

_LAST_NAMES = [
    "Sharma",
    "Patel",
    "Gupta",
    "Singh",
    "Kumar",
    "Joshi",
    "Mehta",
    "Shah",
    "Verma",
    "Yadav",
    "Malhotra",
    "Agarwal",
    "Nair",
    "Pillai",
    "Reddy",
    "Chatterjee",
    "Das",
    "Bose",
    "Roy",
    "Sen",
    "Iyer",
    "Menon",
    "Rao",
    "Desai",
    "Bhatt",
    "Trivedi",
    "Dixit",
    "Kapoor",
    "Khanna",
    "Saxena",
    "Mishra",
    "Tiwari",
    "Pandey",
    "Dwivedi",
    "Pathak",
    "Dubey",
    "Shukla",
    "Srivastava",
    "Bajpai",
    "Awasthi",
    "Prasad",
    "Anand",
    "Kaur",
    "Bhatia",
    "Chopra",
    "Ahuja",
    "Arora",
    "Bajaj",
    "Bansal",
    "Chaudhary",
]

_SKILLS_BY_BRANCH = {
    "Computer Science": [
        "Python, Django, React, PostgreSQL, AWS",
        "Java, Spring Boot, MySQL, Docker, Kubernetes",
        "Go, Kubernetes, CI/CD, Linux, System Design",
        "C++, Algorithms, Competitive Programming, STL",
        "Node.js, Express, MongoDB, TypeScript, REST APIs",
    ],
    "Information Technology": [
        "Vue.js, Flask, PostgreSQL, Redis, REST APIs",
        "PHP, Laravel, MySQL, Linux, Git",
        "React, Node.js, GraphQL, Firebase, AWS",
        "Angular, Java, Spring, Oracle DB",
        "Python, FastAPI, Docker, Terraform",
    ],
    "Electronics": [
        "C, Embedded C, VHDL, Signal Processing, MATLAB",
        "VLSI Design, Verilog, FPGA, Cadence Tools",
        "IoT, Arduino, Raspberry Pi, MQTT, PCB Design",
        "RF Engineering, DSP, MATLAB, Antenna Design",
    ],
    "Mechanical": [
        "AutoCAD, SolidWorks, ANSYS, Lean Manufacturing",
        "CATIA, NX, FEA, Thermodynamics, Fluid Mechanics",
        "PLC, SCADA, Robotic Process Automation",
        "GD&T, Six Sigma, Quality Engineering, Minitab",
    ],
    "Civil": [
        "AutoCAD Civil 3D, STAAD Pro, MS Project, BIM",
        "Revit, Primavera P6, Site Management, GIS",
        "Concrete Design, Steel Design, ETABS, SAP2000",
    ],
    "Chemical": [
        "Aspen HYSYS, ChemCAD, Process Simulation, HAZOP",
        "Reaction Engineering, Process Control, MATLAB",
    ],
    "Electrical": [
        "Power Systems, MATLAB/Simulink, PLC, SCADA",
        "Renewable Energy Systems, ETAP, Power Electronics",
    ],
}

# Branch distribution — must sum to 50
_BRANCH_DIST = (
    ["Computer Science"] * 15
    + ["Information Technology"] * 12
    + ["Electronics"] * 9
    + ["Mechanical"] * 7
    + ["Civil"] * 4
    + ["Chemical"] * 2
    + ["Electrical"] * 1
)


def _build_students() -> list[dict]:
    branches = list(_BRANCH_DIST)
    random.shuffle(branches)
    students = []
    dob_base = date(2001, 1, 1)
    for i in range(50):
        first = _FIRST_NAMES[i]
        last = _LAST_NAMES[i]
        branch = branches[i]
        year = random.choice([2025, 2025, 2025, 2026])
        cgpa = round(random.uniform(6.0, 9.8), 1)
        skills = random.choice(_SKILLS_BY_BRANCH[branch])
        dob = dob_base + timedelta(days=random.randint(0, 730))
        gender = random.choice(["Male", "Female", "Male", "Female", "Male"])
        phone = f"+91-9{random.randint(100_000_000, 999_999_999)}"
        email = f"{first.lower()}.{last.lower()}@university.edu"
        students.append(
            {
                "email": email,
                "password": "Password@123",
                "full_name": f"{first} {last}",
                "branch": branch,
                "year": year,
                "cgpa": cgpa,
                "phone": phone,
                "gender": gender,
                "date_of_birth": dob,
                "skills": skills,
                "is_placed": cgpa >= 8.5 and random.random() < 0.4,
            }
        )
    return students


STUDENTS = _build_students()

# ── Helpers ───────────────────────────────────────────────────────────────────


def _deadline(offset_days: int) -> datetime:
    return datetime.now(UTC) + timedelta(days=offset_days)


def _exists(email: str) -> bool:
    return (
        db.session.query(User.id).filter_by(email=email).scalar() is not None
    )


def _reset() -> None:
    print("  Deleting all rows (admin preserved) …")
    Application.query.delete()
    PlacementDrive.query.delete()
    Company.query.delete()
    Student.query.delete()
    User.query.filter(User.role != UserRole.ADMIN).delete()
    db.session.commit()
    print("  Done.")


def _is_eligible(student: dict, drive: dict) -> bool:
    parts = [
        b.strip()
        for b in drive.get("eligible_branches", "").split(",")
        if b.strip()
    ]
    branch_ok = (
        not parts or parts[0].lower() == "all" or student["branch"] in parts
    )
    cgpa_ok = student["cgpa"] >= drive.get("min_cgpa", 0.0)
    year_ok = not drive.get("max_year") or student["year"] <= drive["max_year"]
    return branch_ok and cgpa_ok and year_ok


# ── Seeding functions ─────────────────────────────────────────────────────────


def seed_companies() -> list[Company]:
    records: list[Company] = []
    for data in COMPANIES:
        if _exists(data["email"]):
            print(f"  skip (exists): {data['email']}")
            user = User.query.filter_by(email=data["email"]).first()
            records.append(user.company_profile)
            continue
        user = User(email=data["email"], role=UserRole.COMPANY)
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()
        company = Company(
            user_id=user.id,
            company_name=data["company_name"],
            hr_name=data["hr_name"],
            hr_contact=data["hr_contact"],
            website=data["website"],
            industry=data["industry"],
            description=data["description"],
            address=data["address"],
            approval_status=data["approval_status"],
        )
        db.session.add(company)
        db.session.flush()
        records.append(company)
        print(f"  created: {data['company_name']} ({data['approval_status']})")
    db.session.commit()
    return records


def seed_drives(companies: list[Company]) -> list[PlacementDrive]:
    records: list[PlacementDrive] = []
    for data in DRIVES:
        company = companies[data["company_index"]]
        drive = PlacementDrive(
            company_id=company.id,
            job_title=data["job_title"],
            job_description=data["job_description"],
            job_location=data.get("job_location"),
            job_type=data.get("job_type"),
            salary_package=data.get("salary_package"),
            eligible_branches=data.get("eligible_branches"),
            min_cgpa=data.get("min_cgpa", 0.0),
            max_year=data.get("max_year"),
            vacancy_count=data.get("vacancy_count", 0),
            other_criteria=data.get("other_criteria"),
            application_deadline=_deadline(data["deadline_offset"]),
            status=data["status"],
        )
        db.session.add(drive)
        db.session.flush()
        records.append(drive)
        print(f"  created: {data['job_title']} [{data['status']}]")
    db.session.commit()
    return records


def seed_students() -> list[Student]:
    records: list[Student] = []
    for data in STUDENTS:
        if _exists(data["email"]):
            print(f"  skip (exists): {data['email']}")
            user = User.query.filter_by(email=data["email"]).first()
            records.append(user.student_profile)
            continue
        user = User(email=data["email"], role=UserRole.STUDENT)
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()
        student = Student(
            user_id=user.id,
            full_name=data["full_name"],
            branch=data["branch"],
            year=data["year"],
            cgpa=data["cgpa"],
            phone=data["phone"],
            gender=data["gender"],
            date_of_birth=data["date_of_birth"],
            skills=data["skills"],
            is_placed=data["is_placed"],
        )
        db.session.add(student)
        db.session.flush()
        records.append(student)
        print(
            f"  created: {data['full_name']} ({data['branch']}, {data['cgpa']})"
        )
    db.session.commit()
    return records


def seed_applications(
    students: list[Student], drives: list[PlacementDrive]
) -> int:
    # Only APPROVED drives accept applications
    approved_indices = [
        i for i, d in enumerate(DRIVES) if d["status"] == DriveStatus.APPROVED
    ]

    # Weighted status pool
    status_pool = (
        [ApplicationStatus.APPLIED] * 5
        + [ApplicationStatus.SHORTLISTED] * 2
        + [ApplicationStatus.SELECTED] * 1
        + [ApplicationStatus.REJECTED] * 2
    )

    # Build unique (student_index, drive_index) pairs based on eligibility
    pairs: set[tuple[int, int]] = set()
    for si, sdata in enumerate(STUDENTS):
        eligible = [
            di for di in approved_indices if _is_eligible(sdata, DRIVES[di])
        ]
        if not eligible:
            continue
        n = random.randint(1, min(5, len(eligible)))
        for di in random.sample(eligible, n):
            pairs.add((si, di))

    count = 0
    for si, di in sorted(pairs):
        try:
            app = Application(
                student_id=students[si].id,
                drive_id=drives[di].id,
                status=random.choice(status_pool),
                applied_at=datetime.now(UTC)
                - timedelta(days=random.randint(1, 30)),
            )
            db.session.add(app)
            db.session.flush()
            count += 1
        except IntegrityError:
            db.session.rollback()
    db.session.commit()
    return count


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the placement portal database."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all company/student/drive/application rows before seeding.",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.reset:
            print("\n[reset]")
            _reset()

        print(f"\n[companies]  ({len(COMPANIES)})")
        companies = seed_companies()

        print(f"\n[drives]  ({len(DRIVES)})")
        drives = seed_drives(companies)

        print(f"\n[students]  ({len(STUDENTS)})")
        students = seed_students()

        print("\n[applications]")
        n_apps = seed_applications(students, drives)

        total = len(companies) + len(drives) + len(students) + n_apps
        print("\n✓ Seeding complete.")
        print(f"  companies    : {len(companies)}")
        print(f"  drives       : {len(drives)}")
        print(f"  students     : {len(students)}")
        print(f"  applications : {n_apps}")
        print(f"  total records: {total}")
        print("\n  All passwords: Password@123")
        print("  Company logins:")
        for c in COMPANIES:
            print(f"    {c['email']}")
        print("  Student format: first.last@university.edu")
        print(
            "    e.g. aarav.sharma@university.edu, priya.patel@university.edu"
        )


if __name__ == "__main__":
    main()
