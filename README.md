# Evasion.mu

Tourism and activities booking web application for Mauritius.

Evasion.mu is a Django-based web application developed as part of the University of Mauritius Web and Mobile Development project.

The platform focuses on tourism services such as hotels, activities and excursions, allowing visitors and customers to browse available services and manage bookings.

## Project Structure

```text
evasion-mu/
│
├── backend/
│   ├── activities/
│   ├── bookings/
│   ├── hotels/
│   ├── payments/
│   ├── reviews/
│   ├── users/
│   ├── wishlist/
│   ├── evasion_project/
│   ├── manage.py
│   └── requirements.txt
│
├── .gitignore
└── README.md

Technologies
- Python 3.11+
- Django 5.2
- PostgreSQL
- HTML / CSS / JavaScript
- Git / GitHub
Django Apps
App	Responsibility
users	User registration, login, logout, profiles and authentication
hotels	Hotels and rooms
activities	Activities, excursions and availability
bookings	Reservations and booking management
payments	Payments and refunds
reviews	Ratings and reviews
wishlist	Customer wishlists


Each app contains its own templates/ and static/ directories.
Requirements
Make sure you have installed:
- Python 3.11 or newer
- PostgreSQL
- Git
Check your Python version:
python --version

Check PostgreSQL:
psql --version

On Windows, if psql is not recognized, PostgreSQL may still be installed. The PostgreSQL bin directory may need to be added to your PATH.

Clone the Repository
Clone the repository:
git clone https://github.com/Romain-N831/evasion-mu.git

Enter the project:
cd evasion-mu

Go to the Django backend:
cd backend

Create a Virtual Environment
Create the virtual environment:
python -m venv venv

Activate it on Windows PowerShell:
.\venv\Scripts\Activate.ps1

If PowerShell blocks the activation script, activate it using:
.\venv\Scripts\activate

Install Dependencies
Make sure the virtual environment is activated.
Then install the project dependencies:
pip install -r requirements.txt

Environment Variables
The project uses a .env file for local configuration.
Create a .env file inside the backend/ directory:
backend/
├── .env
├── manage.py
└── ...

Create the file:
New-Item .env -ItemType File

Add the following:
DB_NAME=evasion_db
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=5433

Replace:
YOUR_POSTGRES_PASSWORD

with your own local PostgreSQL password.
Important
Never commit .env to GitHub.
The .env file is already included in .gitignore.
Each team member should use their own local PostgreSQL credentials.
PostgreSQL Database
Create a local PostgreSQL database called:
evasion_db

The project currently uses PostgreSQL.
Example:
CREATE DATABASE evasion_db;

The PostgreSQL port may be different depending on your local installation.
Update DB_PORT in .env accordingly.
Django Database Setup
After creating your .env file and installing the dependencies, run:
python manage.py check

Then apply the migrations:
python manage.py migrate

Run the Development Server
From the backend/ directory:
python manage.py runserver

The development server will normally be available at:
http://127.0.0.1:8000/

Git Workflow
The main branch is the shared base branch.
Each team member should create their own feature branch from main.
Example:
git checkout main
git pull origin main
git checkout -b feature/hotels

Other examples:
feature/users
feature/activities
feature/bookings
feature/payments
feature/reviews
feature/wishlist

Before Starting Work
Always make sure your local main is up to date:
git checkout main
git pull origin main

Then create your feature branch:
git checkout -b feature/your-feature

Commit Your Changes
Use clear commit messages:
git add .
git commit -m "Add hotel models"

Push your branch:
git push -u origin feature/your-feature

Merging
Team members should work on their own branches.
Changes should be merged into main after review.
Do not work directly on main for feature development.
Important Notes
- Do not commit .env.
- Do not commit passwords or database credentials.
- Each developer uses their own local PostgreSQL database.
- Do not create or modify another teammate's app without coordinating with them.
- Pull the latest main before starting new work.
- Coordinate model relationships between apps before implementing dependent models.
Project Status
Current setup:
- Django project configured
- PostgreSQL configured
- Seven Django apps created
- App-specific templates and static directories created
- Django migrations configured
- Git/GitHub workflow established
<<<<<<< HEAD
Database tables and application-specific models will be defined by the team during development.
=======
Database tables and application-specific models will be defined by the team during development.
>>>>>>> 8ce1b03f47da2e93feb07013d239134819a895fc
