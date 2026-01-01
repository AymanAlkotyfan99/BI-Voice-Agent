import datetime

def log_event(service: str, event: str, details=None):
    print({
        "timestamp": str(datetime.datetime.utcnow()),
        "service": service,
        "event": event,
        "details": details
    })
