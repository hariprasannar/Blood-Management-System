"""
database.py - SQLite database setup and connection manager
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "blood_management.db")


def get_connection():
    """Returns a new SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Creates all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- Donors Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER NOT NULL,
            gender      TEXT    NOT NULL,
            blood_group TEXT    NOT NULL,
            phone       TEXT    UNIQUE NOT NULL,
            email       TEXT,
            city        TEXT    NOT NULL,
            last_donated DATE,
            is_available INTEGER DEFAULT 1,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Acceptors Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acceptors (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            age          INTEGER NOT NULL,
            gender       TEXT    NOT NULL,
            blood_group  TEXT    NOT NULL,
            phone        TEXT    UNIQUE NOT NULL,
            email        TEXT,
            city         TEXT    NOT NULL,
            hospital     TEXT,
            units_needed INTEGER DEFAULT 1,
            urgency      TEXT    DEFAULT 'Normal',
            status       TEXT    DEFAULT 'Pending',
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Blood Inventory Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_inventory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_group TEXT    UNIQUE NOT NULL,
            units       INTEGER DEFAULT 0,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Donations Log Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donation_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id    INTEGER NOT NULL,
            blood_group TEXT    NOT NULL,
            units       INTEGER DEFAULT 1,
            donated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES donors(id)
        )
    """)

    # --- Blood Requests Log Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            acceptor_id  INTEGER NOT NULL,
            donor_id     INTEGER,
            blood_group  TEXT    NOT NULL,
            units        INTEGER DEFAULT 1,
            status       TEXT    DEFAULT 'Pending',
            requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            fulfilled_at DATETIME,
            FOREIGN KEY (acceptor_id) REFERENCES acceptors(id),
            FOREIGN KEY (donor_id)    REFERENCES donors(id)
        )
    """)

    # Seed inventory with all blood groups
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    for bg in blood_groups:
        cursor.execute("""
            INSERT OR IGNORE INTO blood_inventory (blood_group, units)
            VALUES (?, 0)
        """, (bg,))

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")
