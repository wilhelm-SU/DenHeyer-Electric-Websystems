from datetime import datetime, timedelta
from flask import request

# In-memory store for submissions
# { ip_address: [timestamps] }
ipSubmissions = {}

def canSubmit(maxSubmissionsPerDay):
    """Check if the current IP can submit, based on MAX_SUBMISSIONS_PER_DAY."""
    userIp = request.remote_addr
    now = datetime.utcnow()

    # Initialize the list if IP is new
    ipSubmissions.setdefault(userIp, [])

    # Remove timestamps older than 24 hours
    ipSubmissions[userIp] = [t for t in ipSubmissions[userIp] if t > now - timedelta(days=1)]

    if len(ipSubmissions[userIp]) >= maxSubmissionsPerDay:
        return False

    # Record the current submission
    ipSubmissions[userIp].append(now)
    return True