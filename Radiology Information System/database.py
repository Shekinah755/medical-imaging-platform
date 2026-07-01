import sqlite3
import hashlib
from datetime import datetime

# =====================================
# CONNECTION
# =====================================

def get_connection_db():
    conn = sqlite3.connect("radiology.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    return conn, cursor


# =====================================
# HASH PASSWORD
# =====================================

def hash_password(password):
    """
    Converts a plain text password into a secure SHA-256 hash.
    Example: "admin123" becomes a long string of letters and numbers.
    The original password can never be recovered from the hash.
    """
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================
# CREATE DATABASE & ALL TABLES
# =====================================

def create_database_db():
    conn, cursor = get_connection_db()

    # Users table — stores login credentials and role for each staff member
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            UserID   INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            Role     TEXT NOT NULL
                        CHECK(Role IN ('Admin','Radiologist','Technician','Receptionist')),
            FullName TEXT
        )
    """)

    # Patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patients(
            PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name      TEXT NOT NULL,
            Age       INTEGER,
            Sex       TEXT,
            Phone     TEXT,
            UNIQUE(Name, Age, Sex)
        )
    """)

    # Scans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Scans(
            ScanID          INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID       INTEGER,
            ScanType        TEXT,
            BodyRegion      TEXT,
            ScanDate        TEXT,
            ClinicalHistory TEXT,
            ImagePath       TEXT,
            FOREIGN KEY(PatientID)
                REFERENCES Patients(PatientID)
                ON DELETE CASCADE
        )
    """)

    # Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reports(
            ReportID   INTEGER PRIMARY KEY AUTOINCREMENT,
            ScanID     INTEGER,
            Radiologist TEXT,
            Status     TEXT DEFAULT 'Pending',
            ReportText TEXT,
            UNIQUE(ScanID),
            FOREIGN KEY(ScanID)
                REFERENCES Scans(ScanID)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# =====================================
# MIGRATION — adds Phone column if the
# database was created before it existed
# =====================================

def migrate_add_phone_column_db():
    conn, cursor = get_connection_db()
    cursor.execute("PRAGMA table_info(Patients)")
    columns = [row[1] for row in cursor.fetchall()]
    if "Phone" not in columns:
        cursor.execute("ALTER TABLE Patients ADD COLUMN Phone TEXT")
        conn.commit()
    conn.close()


# =====================================
# USER MANAGEMENT
# =====================================

def create_user_db(username, password, role, full_name=""):
    """
    Creates a new user account.
    Returns True on success, False if the username already exists.
    Password is hashed before storage — never stored as plain text.
    """
    conn, cursor = get_connection_db()

    # check if username is already taken
    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False

    hashed = hash_password(password)
    cursor.execute(
        """
        INSERT INTO Users(Username, Password, Role, FullName)
        VALUES (?, ?, ?, ?)
        """,
        (username, hashed, role, full_name),
    )
    conn.commit()
    conn.close()
    return True


def login_db(username, password):
    """
    Checks username and password against the database.

    Returns a dictionary with user info if login is successful:
        {"user_id": 1, "username": "jkwame", "role": "Radiologist", "full_name": "Kwame"}

    Returns None if the username doesn't exist or the password is wrong.
    """
    conn, cursor = get_connection_db()

    hashed = hash_password(password)
    cursor.execute(
        """
        SELECT UserID, Username, Role, FullName
        FROM Users
        WHERE Username = ? AND Password = ?
        """,
        (username, hashed),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id":   row[0],
        "username":  row[1],
        "role":      row[2],
        "full_name": row[3],
    }


def get_all_users_db():
    """Returns all users — used by Admin on the Manage Users page."""
    conn, cursor = get_connection_db()
    cursor.execute("SELECT UserID, Username, Role, FullName FROM Users")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_user_db(user_id):
    conn, cursor = get_connection_db()
    cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


def change_password_db(user_id, new_password):
    conn, cursor = get_connection_db()
    hashed = hash_password(new_password)
    cursor.execute(
        "UPDATE Users SET Password = ? WHERE UserID = ?",
        (hashed, user_id),
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0


# =====================================
# ADD PATIENT
# =====================================

def add_patient_db(name, age, sex, phone=""):
    conn, cursor = get_connection_db()
    cursor.execute(
        "SELECT * FROM Patients WHERE Name = ? AND Age = ? AND Sex = ?",
        (name, age, sex),
    )
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        "INSERT INTO Patients(Name, Age, Sex, Phone) VALUES (?, ?, ?, ?)",
        (name, age, sex, phone),
    )
    conn.commit()
    conn.close()
    return True


# =====================================
# VIEW PATIENTS
# =====================================

def view_patients_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Patients")
    patients = cursor.fetchall()
    conn.close()
    return patients


# =====================================
# SEARCH PATIENT
# =====================================

def search_patient_db(patient_id=None, name=None):
    conn, cursor = get_connection_db()
    if patient_id is not None:
        cursor.execute(
            "SELECT * FROM Patients WHERE PatientID = ?", (patient_id,)
        )
    elif name is not None:
        cursor.execute(
            "SELECT * FROM Patients WHERE Name LIKE ?", (f"%{name}%",)
        )
    else:
        conn.close()
        return []

    patients = cursor.fetchall()
    conn.close()
    return patients


# =====================================
# UPDATE PATIENT
# =====================================

def update_patient_information_db(patient_id, new_name, new_age, new_sex, new_phone=""):
    conn, cursor = get_connection_db()
    cursor.execute(
        """UPDATE Patients
           SET Name = ?, Age = ?, Sex = ?, Phone = ?
           WHERE PatientID = ?""",
        (new_name, new_age, new_sex, new_phone, patient_id),
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0


# =====================================
# DELETE PATIENT
# =====================================

def delete_patient_db(patient_id):
    conn, cursor = get_connection_db()
    cursor.execute("DELETE FROM Patients WHERE PatientID = ?", (patient_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


# =====================================
# ADD SCAN
# =====================================

def add_scan_db(patient_id, scan_type, body_region, scan_date, history, image_path):
    try:
        datetime.strptime(scan_date, "%Y-%m-%d")
    except ValueError:
        return False

    conn, cursor = get_connection_db()

    cursor.execute("SELECT * FROM Patients WHERE PatientID=?", (patient_id,))
    if not cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        "SELECT * FROM Scans WHERE PatientID=? AND ScanType=? AND ScanDate=?",
        (patient_id, scan_type, scan_date),
    )
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        """INSERT INTO Scans
               (PatientID, ScanType, BodyRegion, ScanDate, ClinicalHistory, ImagePath)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (patient_id, scan_type, body_region, scan_date, history, image_path),
    )
    conn.commit()
    conn.close()
    return True


# =====================================
# VIEW SCANS
# =====================================

def view_scans_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Scans")
    scans = cursor.fetchall()
    conn.close()
    return scans


# =====================================
# ADD REPORT
# =====================================

def add_report_db(scan_id, radiologist, status, report_text):
    conn, cursor = get_connection_db()

    cursor.execute("SELECT * FROM Scans WHERE ScanID=?", (scan_id,))
    if not cursor.fetchone():
        conn.close()
        return False

    cursor.execute("SELECT * FROM Reports WHERE ScanID=?", (scan_id,))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        """INSERT INTO Reports(ScanID, Radiologist, Status, ReportText)
           VALUES (?, ?, ?, ?)""",
        (scan_id, radiologist, status, report_text),
    )
    conn.commit()
    conn.close()
    return True


# =====================================
# VIEW REPORTS
# =====================================

def view_reports_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Reports")
    reports = cursor.fetchall()
    conn.close()
    return reports


def view_pending_reports_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Reports WHERE Status='Pending'")
    reports = cursor.fetchall()
    conn.close()
    return reports


def view_completed_reports_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Reports WHERE Status='Completed'")
    reports = cursor.fetchall()
    conn.close()
    return reports


# =====================================
# UPDATE REPORT STATUS
# =====================================

def update_report_status_db(report_id, new_status):
    conn, cursor = get_connection_db()
    cursor.execute(
        "UPDATE Reports SET Status=? WHERE ReportID=?",
        (new_status, report_id),
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0


# =====================================
# FULL PATIENT RECORD
# =====================================

def get_patient_full_record_db(patient_id):
    conn, cursor = get_connection_db()
    cursor.execute("SELECT * FROM Patients WHERE PatientID=?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return None

    cursor.execute("SELECT * FROM Scans WHERE PatientID=?", (patient_id,))
    scans = cursor.fetchall()

    cursor.execute(
        """SELECT Reports.*
           FROM Reports
           JOIN Scans ON Reports.ScanID = Scans.ScanID
           WHERE Scans.PatientID = ?""",
        (patient_id,),
    )
    reports = cursor.fetchall()
    conn.close()
    return {"patient": patient, "scans": scans, "reports": reports}


# =====================================
# DASHBOARD
# =====================================

def dashboard_db():
    conn, cursor = get_connection_db()
    cursor.execute("SELECT COUNT(*) FROM Patients")
    patients = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Scans")
    scans = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Reports")
    reports = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Reports WHERE Status='Pending'")
    pending = cursor.fetchone()[0]
    conn.close()
    return {
        "patients": patients,
        "scans":    scans,
        "reports":  reports,
        "pending":  pending,
    }


# =====================================
# ENTRY POINT
# =====================================

if __name__ == "__main__":
    create_database_db()
    migrate_add_phone_column_db()
    print("Database ready.")