# 🩸 Blood Management System

A complete Python + SQLite blood management system supporting donor registration,
acceptor (recipient) management, blood inventory tracking, compatibility checking,
and analytics reports.

---

## 📁 Project Structure

```
blood_management/
├── main.py                        # Entry point & full demo
├── database.py                    # DB setup & connection manager
├── blood_management.db            # SQLite database (auto-created)
├── services/
│   ├── donor_service.py           # Donor CRUD + donation logging
│   ├── acceptor_service.py        # Acceptor CRUD + blood requests
│   └── inventory_service.py       # Inventory & compatibility logic
└── reports/
    └── analytics.py               # All reports & analytics
```

---

## ▶️ Quick Start

```bash
# No installation needed — uses Python standard library only
python main.py
```

---

## 🔧 Core Features

### Donors
| Function | Description |
|---|---|
| `register_donor(...)` | Register a new donor |
| `get_donor_by_id(id)` | Fetch donor profile by ID |
| `get_donor_by_phone(phone)` | Fetch donor profile by phone |
| `update_donor(id, **fields)` | Update any donor field |
| `delete_donor(id)` | Remove a donor |
| `find_donors_by_blood_group(bg, city)` | Find available donors by blood group |
| `log_donation(donor_id, units)` | Record a donation + update inventory |
| `get_donation_history(donor_id)` | Full donation history for a donor |
| `get_all_donors(available_only)` | List all donors |

### Acceptors
| Function | Description |
|---|---|
| `register_acceptor(...)` | Register a new blood acceptor |
| `get_acceptor_by_id(id)` | Fetch acceptor profile by ID |
| `get_acceptor_by_phone(phone)` | Fetch acceptor profile by phone |
| `update_acceptor(id, **fields)` | Update any acceptor field |
| `delete_acceptor(id)` | Remove an acceptor |
| `request_blood(acceptor_id)` | Submit a blood request |
| `fulfill_request(request_id, donor_id)` | Fulfill a request + deduct inventory |
| `get_request_history(acceptor_id)` | Full request history |
| `get_all_acceptors(status)` | List all acceptors |

### Inventory
| Function | Description |
|---|---|
| `get_inventory()` | Full inventory for all blood groups |
| `get_stock(blood_group)` | Units available for a specific group |
| `add_stock(blood_group, units)` | Manually add units (e.g. donation camp) |
| `check_compatibility(donor_bg, acc_bg)` | Check donor→acceptor compatibility |
| `get_compatible_donors_for_acceptor(bg)` | All compatible available donors |

### Reports
| Function | Description |
|---|---|
| `report_inventory_summary()` | Inventory with low-stock warnings |
| `report_donor_summary()` | Donor stats grouped by blood group |
| `report_acceptor_summary()` | Acceptor stats by status & urgency |
| `report_donation_activity()` | Recent donation logs |
| `report_request_activity()` | Recent blood request logs |
| `report_top_donors()` | Donor leaderboard by units donated |
| `full_report()` | Runs all reports in sequence |

---

## 🩸 Blood Compatibility Reference

| Donor | Can Donate To |
|-------|--------------|
| O-    | Everyone (Universal Donor) |
| O+    | O+, A+, B+, AB+ |
| A-    | A-, A+, AB-, AB+ |
| A+    | A+, AB+ |
| B-    | B-, B+, AB-, AB+ |
| B+    | B+, AB+ |
| AB-   | AB-, AB+ |
| AB+   | AB+ only |

---

## 🗃️ Database Schema

- **donors** — donor profiles with availability tracking
- **acceptors** — recipient profiles with urgency & status
- **blood_inventory** — real-time stock per blood group
- **donation_logs** — timestamped donation history per donor
- **request_logs** — timestamped request history per acceptor

---

## 💡 Usage Example

```python
from database import initialize_database
from services.donor_service import register_donor, log_donation
from services.acceptor_service import register_acceptor, request_blood, fulfill_request
from services.inventory_service import get_compatible_donors_for_acceptor
from reports.analytics import full_report

initialize_database()

# Register a donor
donor = register_donor(
    name="John Doe", age=30, gender="Male",
    blood_group="O+", phone="9000000001", city="Chennai"
)

# Register an acceptor
acceptor = register_acceptor(
    name="Jane Smith", age=45, gender="Female",
    blood_group="O+", phone="9000000002",
    city="Chennai", hospital="Apollo", units_needed=2, urgency="Urgent"
)

# Find compatible donors
matches = get_compatible_donors_for_acceptor("O+", city="Chennai")

# Log a donation
log_donation(donor["id"], units=2)

# Create and fulfill a blood request
request = request_blood(acceptor["id"])
fulfill_request(request["id"], donor_id=donor["id"])

# Run all reports
full_report()
```
