# Radiology Information System (RIS)

## Project Overview

The Radiology Information System (RIS) is a desktop application developed in Python to simplify the management of radiology workflows. The system enables healthcare staff to register patients, manage imaging examinations, create radiology reports, and securely manage user accounts through role-based authentication.

The project was developed as part of my learning in Medical Imaging and software development, with emphasis on database management, graphical user interface (GUI) design, and secure user authentication.

## Features

- User authentication with secure password hashing (SHA-256)
- Role-based access (Administrator, Radiologist, Technician, Receptionist)
- Patient registration and management
- Search, update and delete patient records
- Scan registration and management
- Clinical history recording
- Image path storage
- Radiology report creation
- Report status tracking (Pending / Completed)
- Dashboard displaying system statistics
- SQLite database with foreign key constraints

## Technologies Used

- Python 3
- Tkinter (GUI development)
- SQLite (Database management)
- hashlib (Password hashing for security)
- datetime (Date validation and handling)## Project Structure

Radiology Information System/
│
├── main.py              # Application entry point
├── gui.py               # User interface (Tkinter)
├── database.py          # Database operations and logic
├── radiology.db         # SQLite database (ignored in Git)
├── .gitignore
└── README.md            ## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Shekinah755/medical-imaging-platform/tree/main
```

### 2. Navigate to project folder
```bash
cd Radiology Information System
```

### 3. Run the application
```bash
python main.py
```

## Usage

1. Launch the application using `main.py`
2. Login using admin or staff credentials
3. Register or search for patients
4. Add scan records and clinical history
5. Generate and update radiology reports
6. Monitor system activity via dashboard## Future Improvements


## Future Improvements

- Add DICOM image support for medical imaging compatibility
- Enable PDF export for radiology reports
- Implement appointment scheduling system
- Add audit logs for user activity tracking
- Improve search and filtering functionality
- Upgrade database from SQLite to PostgreSQL for scalability

## Author

Developed by Denuabu Peters Goodness Godslove  
Medical Imaging Student & Cybersecurity Enthusiast