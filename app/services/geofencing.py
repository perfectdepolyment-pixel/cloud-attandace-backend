import math


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Distance in metres between two lat/lng points, accounting for the
    curvature of the earth. Accurate for the short distances relevant to a
    single classroom (see Chapter 3, section 3.5.3 of the project report).
    """
    R = 6371000  # Earth radius in metres
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_within_geofence(
    centre_lat: float, centre_lng: float, student_lat: float, student_lng: float, radius: float
) -> tuple[str, float]:
    distance = haversine_distance(centre_lat, centre_lng, student_lat, student_lng)
    status = "PRESENT" if distance <= radius else "REJECTED"
    return status, distance
