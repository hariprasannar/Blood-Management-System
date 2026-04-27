"""
services/donor_service.py - All donor-related operations
"""

from database import get_connection
from datetime import date

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


def _validate_donor_data(name, age, gender, blood_group, phone, city):
    """Validate donor input fields."""
    if not name or not name.strip():
        raise ValueError("Donor name cannot be empty.")
    if not isinstance(age, int) or not (18 <= age <= 65):
        raise ValueError("Donor age must be between 18 and 65.")
    if gender.capitalize() not in ("Male", "Female", "Other"):
        raise ValueError("Gender must be Male, Female, or Other.")
    if blood_group.upper() not in VALID_BLOOD_GROUPS:
        raise ValueError(f"Invalid blood group. Choose from: {', '.join(VALID_BLOOD_GROUPS)}")
    if not phone or len(phone) < 10:
        raise ValueError("Phone number must be at least 10 digits.")
    if not city or not city.strip():
        raise ValueError("City cannot be empty.")


def register_donor(name, age, gender, blood_group, phone, city, email="", last_donated=None):
    """
    Register a new blood donor.

    Args:
        name        (str): Full name of the donor
        age         (int): Age (must be 18-65)
        gender      (str): Male / Female / Other
        blood_group (str): e.g. "A+", "O-"
        phone       (str): Unique phone number
        city        (str): City of residence
        email       (str): Optional email address
        last_donated(str): Optional date string YYYY-MM-DD

    Returns:
        dict: Newly created donor record
    """
    blood_group = blood_group.upper().strip()
    gender = gender.capitalize().strip()
    _validate_donor_data(name, age, gender, blood_group, phone, city)

    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO donors (name, age, gender, blood_group, phone, email, city, last_donated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), age, gender, blood_group, phone.strip(),
              email.strip() if email else None, city.strip(), last_donated))
        conn.commit()
        donor = conn.execute(
            "SELECT * FROM donors WHERE phone = ?", (phone.strip(),)
        ).fetchone()
        print(f"[Donor] '{name}' registered successfully (ID: {donor['id']}).")
        return dict(donor)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Failed to register donor: {e}")
    finally:
        conn.close()


def get_donor_by_id(donor_id):
    """Fetch a donor's full profile by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM donors WHERE id = ?", (donor_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No donor found with ID {donor_id}.")
    return dict(row)


def get_donor_by_phone(phone):
    """Fetch a donor's full profile by phone number."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM donors WHERE phone = ?", (phone.strip(),)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No donor found with phone {phone}.")
    return dict(row)


def update_donor(donor_id, **fields):
    """
    Update donor profile fields.

    Allowed fields: name, age, gender, blood_group, phone, email, city,
                    last_donated, is_available

    Example:
        update_donor(1, city="Chennai", is_available=0)
    """
    allowed = {"name", "age", "gender", "blood_group", "phone",
               "email", "city", "last_donated", "is_available"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        raise ValueError("No valid fields provided to update.")

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [donor_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE donors SET {set_clause} WHERE id = ?", values)
        conn.commit()
        print(f"[Donor] Donor ID {donor_id} updated: {list(updates.keys())}")
        return get_donor_by_id(donor_id)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Update failed: {e}")
    finally:
        conn.close()


def delete_donor(donor_id):
    """Remove a donor from the system."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
        conn.commit()
        print(f"[Donor] Donor ID {donor_id} deleted.")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Delete failed: {e}")
    finally:
        conn.close()


def get_all_donors(available_only=False):
    """
    Fetch all donors.

    Args:
        available_only (bool): If True, return only donors available to donate.

    Returns:
        list[dict]
    """
    conn = get_connection()
    if available_only:
        rows = conn.execute(
            "SELECT * FROM donors WHERE is_available = 1 ORDER BY name"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM donors ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_donors_by_blood_group(blood_group, city=None):
    """
    Find available donors by blood group, optionally filtered by city.

    Args:
        blood_group (str): e.g. "B+"
        city        (str): Optional city filter

    Returns:
        list[dict]
    """
    blood_group = blood_group.upper().strip()
    conn = get_connection()
    if city:
        rows = conn.execute("""
            SELECT * FROM donors
            WHERE blood_group = ? AND city LIKE ? AND is_available = 1
            ORDER BY last_donated ASC
        """, (blood_group, f"%{city.strip()}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM donors
            WHERE blood_group = ? AND is_available = 1
            ORDER BY last_donated ASC
        """, (blood_group,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_donation(donor_id, units=1):
    """
    Record a blood donation and update inventory.

    Args:
        donor_id (int): Donor's ID
        units    (int): Units donated (default 1)
    """
    donor = get_donor_by_id(donor_id)
    today = str(date.today())

    conn = get_connection()
    try:
        # Log donation
        conn.execute("""
            INSERT INTO donation_logs (donor_id, blood_group, units)
            VALUES (?, ?, ?)
        """, (donor_id, donor["blood_group"], units))

        # Update donor's last_donated and mark temporarily unavailable
        conn.execute("""
            UPDATE donors SET last_donated = ?, is_available = 0
            WHERE id = ?
        """, (today, donor_id))

        # Update inventory
        conn.execute("""
            UPDATE blood_inventory
            SET units = units + ?, updated_at = CURRENT_TIMESTAMP
            WHERE blood_group = ?
        """, (units, donor["blood_group"]))

        conn.commit()
        print(f"[Donation] {units} unit(s) of {donor['blood_group']} logged for donor ID {donor_id}.")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Donation log failed: {e}")
    finally:
        conn.close()


def get_donation_history(donor_id):
    """Get full donation history for a donor."""
    get_donor_by_id(donor_id)  # validates donor exists
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM donation_logs WHERE donor_id = ?
        ORDER BY donated_at DESC
    """, (donor_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
