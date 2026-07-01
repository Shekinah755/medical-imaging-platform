"""
setup_users.py
==============
Run this ONCE before launching the app for the first time.
It creates the database tables and seeds one account for each role
so you can log in and test immediately.

After setup, the Admin can create more accounts from inside the app.

Usage:
    python setup_users.py
"""

from database import create_database_db, migrate_add_phone_column_db, create_user_db

def main():
    print("Setting up database...")
    create_database_db()
    migrate_add_phone_column_db()

    # Default accounts — change these passwords before going live!
    accounts = [
        ("admin",        "admin123",  "Admin",        "System Administrator"),
        ("radiologist1", "radio123",  "Radiologist",  "Dr. Kwame Owusu"),
        ("technician1",  "tech123",   "Technician",   "Kofi Mensah"),
        ("reception1",   "recep123",  "Receptionist", "Ama Asante"),
    ]

    print("\nCreating accounts:")
    for username, password, role, full_name in accounts:
        created = create_user_db(username, password, role, full_name)
        if created:
            print(f"  ✔  {role:<15} username: {username:<20} password: {password}")
        else:
            print(f"  ⚠  {username} already exists — skipped")

    print("\nSetup complete. You can now run:  python gui.py")
    print("\nIMPORTANT: Change the default passwords after first login!")

if __name__ == "__main__":
    main()