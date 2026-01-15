from datetime import datetime
import itertools

_order_counter = itertools.count(1)


def generate_order_id() -> str:
    """
    Format: ORD-YYYYMMDD-####
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    seq = next(_order_counter)
    return f"ORD-{today}-{seq:04d}"


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat()
