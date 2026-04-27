"""
reports/analytics.py - Reports and analytics for the Blood Management System
"""

from database import get_connection


def _separator(title="", width=60, char="="):
    if title:
        side = (width - len(title) - 2) // 2
        print(f"\n{char * side} {title} {char * side}")
    else:
        print(char * width)


def report_inventory_summary():
    """
    Print a full inventory summary showing units per blood group
    with a LOW STOCK warning when units < 5.
    """
    _separator("BLOOD INVENTORY REPORT")
    conn = get_connection()
    rows = conn.execute(
        "SELECT blood_group, units, updated_at FROM blood_inventory ORDER BY blood_group"
    ).fetchall()
    conn.close()

    total = 0
    print(f"{'Blood Group':<15} {'Units':>8}  {'Status'}")
    print("-" * 40)
    for r in rows:
        status = "⚠ LOW STOCK" if r["units"] < 5 else "OK"
        print(f"{r['blood_group']:<15} {r['units']:>8}  {status}")
        total += r["units"]
    print("-" * 40)
    print(f"{'TOTAL':<15} {total:>8}")
    _separator()
    return [dict(r) for r in rows]


def report_donor_summary():
    """
    Print a donor statistics summary grouped by blood group.
    """
    _separator("DONOR SUMMARY REPORT")
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) as c FROM donors").fetchone()["c"]
    available = conn.execute(
        "SELECT COUNT(*) as c FROM donors WHERE is_available = 1"
    ).fetchone()["c"]

    rows = conn.execute("""
        SELECT blood_group,
               COUNT(*) as total,
               SUM(is_available) as available
        FROM donors
        GROUP BY blood_group
        ORDER BY blood_group
    """).fetchall()
    conn.close()

    print(f"Total Donors   : {total}")
    print(f"Available Now  : {available}")
    print(f"Unavailable    : {total - available}")
    print()
    print(f"{'Blood Group':<14} {'Total':>8} {'Available':>12}")
    print("-" * 38)
    for r in rows:
        print(f"{r['blood_group']:<14} {r['total']:>8} {r['available']:>12}")
    _separator()
    return [dict(r) for r in rows]


def report_acceptor_summary():
    """
    Print an acceptor (recipient) statistics summary.
    """
    _separator("ACCEPTOR SUMMARY REPORT")
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) as c FROM acceptors").fetchone()["c"]

    by_status = conn.execute("""
        SELECT status, COUNT(*) as count
        FROM acceptors GROUP BY status
    """).fetchall()

    by_urgency = conn.execute("""
        SELECT urgency, COUNT(*) as count
        FROM acceptors WHERE status = 'Pending'
        GROUP BY urgency
    """).fetchall()

    conn.close()

    print(f"Total Acceptors: {total}\n")

    print("By Status:")
    for r in by_status:
        print(f"  {r['status']:<15}: {r['count']}")

    print("\nPending by Urgency:")
    for r in by_urgency:
        print(f"  {r['urgency']:<15}: {r['count']}")

    _separator()
    return {"total": total, "by_status": [dict(r) for r in by_status]}


def report_donation_activity(limit=20):
    """
    Print the most recent donation activity log.

    Args:
        limit (int): Number of recent records to show (default 20)
    """
    _separator("RECENT DONATION ACTIVITY")
    conn = get_connection()
    rows = conn.execute(f"""
        SELECT dl.id, d.name as donor_name, dl.blood_group,
               dl.units, dl.donated_at
        FROM donation_logs dl
        JOIN donors d ON dl.donor_id = d.id
        ORDER BY dl.donated_at DESC
        LIMIT {limit}
    """).fetchall()
    conn.close()

    if not rows:
        print("No donations recorded yet.")
    else:
        print(f"{'ID':>4} {'Donor':<22} {'Blood':>6} {'Units':>6}  {'Date'}")
        print("-" * 56)
        for r in rows:
            print(f"{r['id']:>4} {r['donor_name']:<22} {r['blood_group']:>6} "
                  f"{r['units']:>6}  {r['donated_at'][:10]}")
    _separator()
    return [dict(r) for r in rows]


def report_request_activity(limit=20):
    """
    Print recent blood request logs.

    Args:
        limit (int): Number of recent records to show (default 20)
    """
    _separator("RECENT BLOOD REQUEST ACTIVITY")
    conn = get_connection()
    rows = conn.execute(f"""
        SELECT rl.id,
               a.name  as acceptor_name,
               d.name  as donor_name,
               rl.blood_group,
               rl.units,
               rl.status,
               rl.requested_at
        FROM request_logs rl
        JOIN acceptors a ON rl.acceptor_id = a.id
        LEFT JOIN donors d ON rl.donor_id = d.id
        ORDER BY rl.requested_at DESC
        LIMIT {limit}
    """).fetchall()
    conn.close()

    if not rows:
        print("No blood requests recorded yet.")
    else:
        print(f"{'ID':>4} {'Acceptor':<20} {'Donor':<18} {'BG':>4} {'Units':>5}  {'Status':<12}  {'Date'}")
        print("-" * 80)
        for r in rows:
            donor_name = r["donor_name"] or "—"
            print(f"{r['id']:>4} {r['acceptor_name']:<20} {donor_name:<18} "
                  f"{r['blood_group']:>4} {r['units']:>5}  {r['status']:<12}  {r['requested_at'][:10]}")
    _separator()
    return [dict(r) for r in rows]


def report_top_donors(limit=10):
    """
    Print a leaderboard of top donors by total units donated.

    Args:
        limit (int): Number of donors to show (default 10)
    """
    _separator("TOP DONORS LEADERBOARD")
    conn = get_connection()
    rows = conn.execute(f"""
        SELECT d.name, d.blood_group, d.city,
               COUNT(dl.id)  as times_donated,
               SUM(dl.units) as total_units
        FROM donation_logs dl
        JOIN donors d ON dl.donor_id = d.id
        GROUP BY dl.donor_id
        ORDER BY total_units DESC
        LIMIT {limit}
    """).fetchall()
    conn.close()

    if not rows:
        print("No donation data yet.")
    else:
        print(f"{'Rank':<6} {'Name':<22} {'Blood':>6} {'City':<16} {'Donations':>10} {'Units':>6}")
        print("-" * 70)
        for i, r in enumerate(rows, 1):
            print(f"{i:<6} {r['name']:<22} {r['blood_group']:>6} {r['city']:<16} "
                  f"{r['times_donated']:>10} {r['total_units']:>6}")
    _separator()
    return [dict(r) for r in rows]


def full_report():
    """Run all reports in sequence."""
    report_inventory_summary()
    report_donor_summary()
    report_acceptor_summary()
    report_donation_activity()
    report_request_activity()
    report_top_donors()
