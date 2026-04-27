"""
main.py - Blood Management System
Entry point: demonstrates all features with sample data.

Run with:
    python main.py
"""

import sys
import os

# Ensure local imports work regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))

from database import initialize_database
from services.donor_service   import (
    register_donor, get_donor_by_id, get_donor_by_phone,
    update_donor, find_donors_by_blood_group, log_donation,
    get_donation_history, get_all_donors
)
from services.acceptor_service import (
    register_acceptor, get_acceptor_by_id, get_acceptor_by_phone,
    update_acceptor, request_blood, fulfill_request,
    get_request_history, get_all_acceptors
)
from services.inventory_service import (
    get_inventory, get_stock, add_stock,
    check_compatibility, get_compatible_donors_for_acceptor
)
from reports.analytics import full_report


def section(title):
    print(f"\n{'#' * 60}")
    print(f"  {title}")
    print(f"{'#' * 60}")


def demo():
    """Full end-to-end demo of the Blood Management System."""

    # ── 1. Initialize Database ──────────────────────────────────────
    section("1. Initializing Database")
    initialize_database()

    # ── 2. Register Donors ──────────────────────────────────────────
    section("2. Registering Donors")

    d1 = register_donor(
        name="Arjun Kumar", age=28, gender="Male",
        blood_group="O+", phone="9876543210",
        city="Coimbatore", email="arjun@example.com",
        last_donated="2024-10-15"
    )

    d2 = register_donor(
        name="Priya Sharma", age=34, gender="Female",
        blood_group="A+", phone="9123456789",
        city="Chennai", email="priya@example.com"
    )

    d3 = register_donor(
        name="Ravi Menon", age=45, gender="Male",
        blood_group="B-", phone="9988776655",
        city="Coimbatore"
    )

    d4 = register_donor(
        name="Sneha Nair", age=22, gender="Female",
        blood_group="O-", phone="9001122334",
        city="Bangalore"
    )

    # ── 3. Register Acceptors ───────────────────────────────────────
    section("3. Registering Acceptors")

    a1 = register_acceptor(
        name="Vijay Reddy", age=52, gender="Male",
        blood_group="O+", phone="8011223344",
        city="Coimbatore", hospital="PSG Hospital",
        units_needed=2, urgency="Urgent"
    )

    a2 = register_acceptor(
        name="Lakshmi Devi", age=38, gender="Female",
        blood_group="A+", phone="8099887766",
        city="Chennai", hospital="Apollo Hospital",
        units_needed=1, urgency="Normal"
    )

    a3 = register_acceptor(
        name="Karthik Raj", age=25, gender="Male",
        blood_group="B-", phone="8055443322",
        city="Coimbatore", hospital="KG Hospital",
        units_needed=3, urgency="Critical"
    )

    # ── 4. View Profiles ────────────────────────────────────────────
    section("4. Viewing Profiles")

    print("\n-- Donor by ID --")
    donor_profile = get_donor_by_id(d1["id"])
    for k, v in donor_profile.items():
        print(f"  {k:<18}: {v}")

    print("\n-- Acceptor by Phone --")
    acc_profile = get_acceptor_by_phone("8011223344")
    for k, v in acc_profile.items():
        print(f"  {k:<18}: {v}")

    # ── 5. Update Profiles ──────────────────────────────────────────
    section("5. Updating Profiles")

    update_donor(d1["id"], city="Coimbatore", is_available=1)
    update_acceptor(a3["id"], urgency="Critical", units_needed=4)

    # ── 6. Blood Compatibility Check ────────────────────────────────
    section("6. Blood Compatibility Checks")

    pairs = [("O-", "AB+"), ("A+", "B+"), ("B-", "B+"), ("O+", "O+")]
    for donor_bg, acc_bg in pairs:
        result = check_compatibility(donor_bg, acc_bg)
        print(f"  {donor_bg} → {acc_bg}: {'✓ Compatible' if result else '✗ Incompatible'}")

    # ── 7. Find Donors by Blood Group ───────────────────────────────
    section("7. Finding Donors by Blood Group")

    print("\n-- Available O+ donors in Coimbatore --")
    matches = find_donors_by_blood_group("O+", city="Coimbatore")
    for m in matches:
        print(f"  {m['name']} | {m['blood_group']} | {m['city']} | Ph: {m['phone']}")

    print("\n-- Compatible donors for acceptor needing B- --")
    compatible = get_compatible_donors_for_acceptor("B-")
    for c in compatible:
        print(f"  {c['name']} | {c['blood_group']} | {c['city']}")

    # ── 8. Log Donations ────────────────────────────────────────────
    section("8. Logging Donations")

    log_donation(d1["id"], units=2)
    log_donation(d2["id"], units=1)
    log_donation(d3["id"], units=1)
    log_donation(d4["id"], units=3)

    print("\n-- Donation history for Arjun --")
    history = get_donation_history(d1["id"])
    for h in history:
        print(f"  Units: {h['units']} | Blood: {h['blood_group']} | Date: {h['donated_at'][:10]}")

    # ── 9. Inventory Status ─────────────────────────────────────────
    section("9. Blood Inventory Status")

    inventory = get_inventory()
    print(f"\n{'Blood Group':<14} {'Units':>6}")
    print("-" * 22)
    for item in inventory:
        print(f"  {item['blood_group']:<12} {item['units']:>6}")

    print(f"\n  O+ stock : {get_stock('O+')}")
    print(f"  A+ stock : {get_stock('A+')}")

    # Manually add external donation camp stock
    add_stock("AB+", 5)
    add_stock("O-", 10)

    # ── 10. Blood Requests ──────────────────────────────────────────
    section("10. Blood Requests")

    req1 = request_blood(a1["id"])
    req2 = request_blood(a2["id"])
    req3 = request_blood(a3["id"])

    # Fulfill request 1 using donor 1
    fulfill_request(req1["id"], donor_id=d1["id"])

    print("\n-- Request history for Vijay Reddy --")
    req_history = get_request_history(a1["id"])
    for r in req_history:
        print(f"  Status: {r['status']} | Blood: {r['blood_group']} | "
              f"Units: {r['units']} | Donor ID: {r['donor_id']}")

    # ── 11. List All Records ────────────────────────────────────────
    section("11. All Donors & Acceptors")

    print(f"\nAll Donors ({len(get_all_donors())} total):")
    for d in get_all_donors():
        avail = "Available" if d["is_available"] else "Unavailable"
        print(f"  [{d['id']}] {d['name']} | {d['blood_group']} | {d['city']} | {avail}")

    print(f"\nPending Acceptors:")
    for a in get_all_acceptors(status="Pending"):
        print(f"  [{a['id']}] {a['name']} | {a['blood_group']} | "
              f"{a['urgency']} | Units needed: {a['units_needed']}")

    # ── 12. Full Analytics Report ───────────────────────────────────
    section("12. Full Analytics Reports")
    full_report()

    print("\n✅ Blood Management System demo completed successfully!\n")


if __name__ == "__main__":
    demo()
