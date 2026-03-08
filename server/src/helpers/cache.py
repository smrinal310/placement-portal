from flask_caching import Cache

cache = Cache()


def invalidate_cache(path_prefixes):

    if not hasattr(cache.cache, "_write_client"):
        return

    redis_client = cache.cache._write_client
    for prefix in path_prefixes:
        match_pattern = f"*{prefix}*"

        cursor = "0"
        while cursor != 0:
            cursor, keys = redis_client.scan(
                cursor=cursor, match=match_pattern, count=100
            )
            if keys:
                redis_client.delete(*keys)


def invalidate_company_cache():
    invalidate_cache(
        [
            "api/admin/companies",
            "api/admin/dashboard",
            "api/company/profile",
            "api/company/dashboard",
        ]
    )


def invalidate_student_cache():
    invalidate_cache(
        [
            "api/admin/students",
            "api/admin/dashboard",
            "api/student/profile",
            "api/student/dashboard",
        ]
    )


def invalidate_drive_cache():
    invalidate_cache(
        [
            "api/admin/drives",
            "api/admin/dashboard",
            "api/company/drives",
            "api/company/dashboard",
            "api/student/drives",
            "api/student/dashboard",
        ]
    )


def invalidate_application_cache():
    invalidate_cache(
        [
            "api/admin/applications",
            "api/admin/dashboard",
            "api/company/drives",
            "api/company/dashboard",
            "api/student/applications",
            "api/student/dashboard",
        ]
    )
