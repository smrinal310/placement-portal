def check_eligibility(student, drive) -> tuple[bool, str | None]:
    """Check if a student meets the eligibility criteria for a drive.

    Returns (is_eligible: bool, reason: str | None).
    """
    # Check CGPA
    if drive.min_cgpa and student.cgpa < drive.min_cgpa:
        return False, (
            f"CGPA {student.cgpa} is below the required {drive.min_cgpa}"
        )

    # Check branch eligibility
    if drive.eligible_branches:
        eligible = [
            b.strip().lower() for b in drive.eligible_branches.split(",")
        ]
        if student.branch.lower() not in eligible:
            return False, (
                f"Your branch {student.branch} is not eligible for this drive"
            )

    # Check year
    min_year = drive.min_year or 1
    max_year = drive.max_year or 4
    if not (min_year <= student.year <= max_year):
        return False, (
            f"Your year {student.year} does not meet the requirement"
        )

    return True, None
