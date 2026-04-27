"""
services/inventory_service.py - Blood inventory management
"""

from database import get_connection

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


def get_inventory():
    """
    Returns current blood inventory for all blood groups.

    Returns:
        list[dict]: Each entry has blood_group, units, updated_at
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM blood_inventory ORDER BY blood_group"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stock(blood_group):
    """
    Get available units for a specific blood group.

    Args:
        blood_group (str): e.g. "A+"

    Returns:
        int: Number of available units
    """
    blood_group = blood_group.upper().strip()
    if blood_group not in VALID_BLOOD_GROUPS:
        raise ValueError(f"Invalid blood group: {blood_group}")
    conn = get_connection()
    row = conn.execute(
        "SELECT units FROM blood_inventory WHERE blood_group = ?",
        (blood_group,)
    ).fetchone()
    conn.close()
    return row["units"] if row else 0


def add_stock(blood_group, units):
    """
    Manually add units to inventory (e.g. from external donation camp).

    Args:
        blood_group (str): e.g. "O-"
        units       (int): Units to add
    """
    blood_group = blood_group.upper().strip()
    if blood_group not in VALID_BLOOD_GROUPS:
        raise ValueError(f"Invalid blood group: {blood_group}")
    if not isinstance(units, int) or units <= 0:
        raise ValueError("Units must be a positive integer.")

    conn = get_connection()
    try:
        conn.execute("""
            UPDATE blood_inventory
            SET units = units + ?, updated_at = CURRENT_TIMESTAMP
            WHERE blood_group = ?
        """, (units, blood_group))
        conn.commit()
        print(f"[Inventory] Added {units} unit(s) of {blood_group}. "
              f"New total: {get_stock(blood_group)}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Stock update failed: {e}")
    finally:
        conn.close()


def check_compatibility(donor_group, acceptor_group):
    """
    Check if a donor blood group is compatible with an acceptor's blood group.

    Standard ABO + Rh compatibility rules.

    Args:
        donor_group    (str): Donor's blood group
        acceptor_group (str): Acceptor's blood group

    Returns:
        bool
    """
    compatibility_map = {
        "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+":  ["O+", "A+", "B+", "AB+"],
        "A-":  ["A-", "A+", "AB-", "AB+"],
        "A+":  ["A+", "AB+"],
        "B-":  ["B-", "B+", "AB-", "AB+"],
        "B+":  ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"],
    }
    donor_group    = donor_group.upper().strip()
    acceptor_group = acceptor_group.upper().strip()
    compatible_with = compatibility_map.get(donor_group, [])
    return acceptor_group in compatible_with


def get_compatible_donors_for_acceptor(acceptor_blood_group, city=None):
    """
    Find all available donors whose blood is compatible with the acceptor.

    Args:
        acceptor_blood_group (str): Acceptor's blood group
        city                 (str): Optional city filter

    Returns:
        list[dict]: Matching donor records
    """
    acceptor_blood_group = acceptor_blood_group.upper().strip()

    all_groups = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
    compatible_donor_groups = [
        g for g in all_groups
        if check_compatibility(g, acceptor_blood_group)
    ]

    if not compatible_donor_groups:
        return []

    placeholders = ", ".join("?" * len(compatible_donor_groups))
    conn = get_connection()

    if city:
        rows = conn.execute(f"""
            SELECT * FROM donors
            WHERE blood_group IN ({placeholders})
              AND is_available = 1
              AND city LIKE ?
            ORDER BY last_donated ASC
        """, compatible_donor_groups + [f"%{city.strip()}%"]).fetchall()
    else:
        rows = conn.execute(f"""
            SELECT * FROM donors
            WHERE blood_group IN ({placeholders})
              AND is_available = 1
            ORDER BY last_donated ASC
        """, compatible_donor_groups).fetchall()

    conn.close()
    return [dict(r) for r in rows]
