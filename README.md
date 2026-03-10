# Apartment Rental Management System

## About the Project
This is a personal project aimed at building a comprehensive apartment and room rental management platform. 
The system allows landlords to post property listings, while tenants can easily search, view detailed information, browse images, check map locations, and contact hosts directly. Additionally, the platform provides a centralized administrative interface for convenient system management.

---

## Key Objectives
- Develop an online **apartment/room rental** platform.
- Enable **tenants** to search, filter, and view property details seamlessly.
- Allow **landlords** to easily manage their property listings.
- Centralize system management for **Administrators** via the **Django Admin Site**.
- Ensure robust **security and role-based access control (RBAC)**.

---

## Tech Stack
- **Backend**: Django + Django REST Framework
- **Frontend**: ReactJS
- **Database**: MySQL
- **Deployment**: PythonAnywhere / Railway / Render
- **Third-party APIs**: Google Maps API (Location integration)
- **Real-time Chat**: Firebase (Tenant-landlord communication)
- **Authentication & Security**: OAuth2
  <img width="1270" height="679" alt="image" src="https://github.com/user-attachments/assets/42ee8acf-8f9d-4713-b103-7e2ae7e4de00" />

---

## Core Features

### General Users
- **Authentication**: Register / Login (Tenant, Landlord, Admin).
- **Profile Management**: Update personal info, avatar, phone number, etc.
- **Listing Details**: View descriptions, images, Google Maps location, and contact info.
- **Contact Host**: Reach out via provided contact info or real-time chat.

### Landlords (Hosts)
- **Create Listings**: Post properties with titles, descriptions, images, rental prices, locations, and amenities.
- **Listing Management**: Add, update, delete, or toggle visibility (e.g., hide when a room is rented).

### Tenants
- **Search**: Find properties by keywords, address, or room type.
- **Filter**: Narrow down listings by specific criteria (price range, area, location, amenities).

### Administrators (Admins)
- Manage all **users** and **listings** centrally via Django Admin.
- Suspend accounts or remove listings that violate policies.
- **System Dashboard**: Visualize data and generate statistical charts.

---

## System Architecture
![ReactJS](https://github.com/user-attachments/assets/fa871d99-dcb9-4385-977e-ee0602b2105c)

---

## Getting Started

### Clone the repository
```bash
git clone [https://github.com/ThuanProfessor/apartment-rental-django.git](https://github.com/ThuanProfessor/apartment-rental-django.git)
cd apartment-rental-django
```

### Create a virtual environment
```bash
python -m venv venv
```

### Activate the virtual environment
```bash
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### Install required Python dependencies
```bash
pip install -r requirements.txt
```

### Run database migrations to create MySQL tables
```bash
python manage.py migrate
```

### Start the Django development server
```bash
python manage.py runserver
```

##  License

This project is licensed under multiple open source licenses:

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

##  Support

For support and inquiries, please contact:
- 📧 Email: [hoangthuandev04@gmail.com](mailto:hoangthuandev04@gmail.com)
