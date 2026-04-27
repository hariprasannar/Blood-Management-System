"""
services/acceptor_service.py - All acceptor (blood recipient) operations
"""

from database import get_connection

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
VALID_URGENCY     = {"Normal", "Urgent", "Critical"}


def _validate_acceptor_data(name, age, gender, blood_group, phone, city, units_needed, urgency):
    if not name or not name.strip():
        raise ValueError("Acceptor name cannot be empty.")
    if not isinstance(age, int) or age <= 0:
        raise ValueError("Age must be a positive integer.")
    if gender.capitalize() not in ("Male", "Female", "Other"):
        raise ValueError("Gender must be Male, Female, or Other.")
    if blood_group.upper() not in VALID_BLOOD_GROUPS:
        raise ValueError(f"Invalid blood group. Choose from: {', '.join(VALID_BLOOD_GROUPS)}")
    if not phone or len(phone) < 10:
        raise ValueError("Phone number must be at least 10 digits.")
    if not city or not city.strip():
        raise ValueError("City cannot be empty.")
    if not isinstance(units_needed, int) or units_needed <= 0:
        raise ValueError("Units needed must be a positive integer.")
    if urgency.capitalize() not in VALID_URGENCY:
        raise ValueError(f"Urgency must be one of: {', '.join(VALID_URGENCY)}")


def register_acceptor(name, age, gender, blood_group, phone, city,
                       hospital="", units_needed=1, urgency="Normal", email=""):
    """
    Register a new blood acceptor (recipient).

    Args:
        name         (str): Full name
        age          (int): Age
        gender       (str): Male / Female / Other
        blood_group  (str): Required blood group e.g. "O+"
        phone        (str): Unique phone number
        city         (str): City
        hospital     (str): Optional hospital name
        units_needed (int): Number of blood units required
        urgency      (str): Normal / Urgent / Critical
        email        (str): Optional email

    Returns:
        dict: Newly created acceptor record
    """
    blood_group = blood_group.upper().strip()
    gender      = gender.capitalize().strip()
    urgency     = urgency.capitalize().strip()

    _validate_acceptor_data(name, age, gender, blood_group, phone, city, units_needed, urgency)

    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO acceptors
                (name, age, gender, blood_group, phone, email, city, hospital, units_needed, urgency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), age, gender, blood_group, phone.strip(),
              email.strip() if email else None, city.strip(),
              hospital.strip() if hospital else None, units_needed, urgency))
        conn.commit()
        acceptor = conn.execute(
            "SELECT * FROM acceptors WHERE phone = ?", (phone.strip(),)
        ).fetchone()
        print(f"[Acceptor] '{name}' registered successfully (ID: {acceptor['id']}).")
        return dict(acceptor)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to register acceptor: {e}")
    finally:
        conn.close()


def get_acceptor_by_id(acceptor_id):
    """Fetch an acceptor's full profile by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM acceptors WHERE id = ?", (acceptor_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No acceptor found with ID {acceptor_id}.")
    return dict(row)


def get_acceptor_by_phone(phone):
    """Fetch an acceptor's full profile by phone number."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM acceptors WHERE phone = ?", (phone.strip(),)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No acceptor found with phone {phone}.")
    return dict(row)


def update_acceptor(acceptor_id, **fields):
    """
    Update acceptor profile fields.

    Allowed: name, age, gender, blood_group, phone, email, city,
             hospital, units_needed, urgency, status

    Example:
        update_acceptor(2, urgency="Critical", units_needed=3)
    """
    allowed = {"name", "age", "gender", "blood_group", "phone", "email",
               "city", "hospital", "units_needed", "urgency", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        raise ValueError("No valid fields provided to update.")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [acceptor_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE acceptors SET {set_clause} WHERE id = ?", values)
        conn.commit()
        print(f"[Acceptor] Acceptor ID {acceptor_id} updated: {list(updates.keys())}")
        return get_acceptor_by_id(acceptor_id)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Update failed: {e}")
    finally:
        conn.close()


def delete_acceptor(acceptor_id):
    """Remove an acceptor from the system."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM acceptors WHERE id = ?", (acceptor_id,))
        conn.commit()
        print(f"[Acceptor] Acceptor ID {acceptor_id} deleted.")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Delete failed: {e}")
    finally:
        conn.close()


def get_all_acceptors(status=None):
    """
    Fetch all acceptors, optionally filtered by status.

    Args:
        status (str): e.g. "Pending", "Fulfilled", "Cancelled"

    Returns:
        list[dict]
    """
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM acceptors WHERE status = ? ORDER BY registered_at DESC",
            (status.capitalize(),)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM acceptors ORDER BY registered_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def request_blood(acceptor_id):
    """
    Submit a blood request for an acceptor. Creates a request log entry.

    Args:
        acceptor_id (int): Acceptor's ID

    Returns:
        dict: The request log entry
    """
    acceptor = get_acceptor_by_id(acceptor_id)

    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO request_logs (acceptor_id, blood_group, units, status)
            VALUES (?, ?, ?, 'Pending')
        """, (acceptor_id, acceptor["blood_group"], acceptor["units_needed"]))
        conn.commit()

        log = conn.execute(
            "SELECT * FROM request_logs WHERE acceptor_id = ? ORDER BY requested_at DESC LIMIT 1",
            (acceptor_id,)
        ).fetchone()
        print(f"[Request] Blood request logged for acceptor ID {acceptor_id} "
              f"({acceptor['blood_group']} x{acceptor['units_needed']}).")
        return dict(log)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Blood request failed: {e}")
    finally:
        conn.close()


def fulfill_request(request_id, donor_id):
    """
    Mark a blood request as fulfilled by a specific donor.

    Args:
        request_id (int): Request log ID
        donor_id   (int): Donor who fulfilled the request
    """
    conn = get_connection()
    try:
        req = conn.execute(
            "SELECT * FROM request_logs WHERE id = ?", (request_id,)
        ).fetchone()
        if not req:
            raise ValueError(f"No request found with ID {request_id}.")

        # Deduct from inventory
        inv = conn.execute(
            "SELECT units FROM blood_inventory WHERE blood_group = ?",
            (req["blood_group"],)
        ).fetchone()

        if not inv or inv["units"] < req["units"]:
            raise RuntimeError(
                f"Insufficient inventory for {req['blood_group']}. "
                f"Available: {inv['units'] if inv else 0}, Needed: {req['units']}"
            )

        conn.execute("""
            UPDATE blood_inventory
            SET units = units - ?, updated_at = CURRENT_TIMESTAMP
            WHERE blood_group = ?
        """, (req["units"], req["blood_group"]))

        conn.execute("""
            UPDATE request_logs
            SET donor_id = ?, status = 'Fulfilled', fulfilled_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (donor_id, request_id))

        conn.execute(
            "UPDATE acceptors SET status = 'Fulfilled' WHERE id = ?",
            (req["acceptor_id"],)
        )

        conn.commit()
        print(f"[Request] Request ID {request_id} fulfilled by donor ID {donor_id}.")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Fulfill request failed: {e}")
    finally:
        conn.close()


def get_request_history(acceptor_id):
    """Get full request history for an acceptor."""
    get_acceptor_by_id(acceptor_id)
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM request_logs WHERE acceptor_id = ?
        ORDER BY requested_at DESC
    """, (acceptor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
