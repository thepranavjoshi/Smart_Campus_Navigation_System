# Smart Campus Navigation System (SCNS)

A Flask-based campus navigation web application with authentication, role-based access control, pathfinding, notifications, and analytics dashboard.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scns_flask_project
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

Or use your local IP (e.g., `http://192.168.x.x:5000`) to access from other devices.

---

## 👤 Test Accounts

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| admin | admin123 | Administrator | Full access |
| faculty | faculty123 | Faculty | Content management |
| student | student123 | Student | Navigation + notifications |
| visitor | visitor123 | Visitor | Basic navigation |

**Note:** On first login, check the terminal/console for the MFA OTP code.

---

## 🎯 Features

### Authentication & Security
- ✅ Username/password login with SHA256 hashing
- ✅ Multi-Factor Authentication (OTP via console)
- ✅ Role-based access control (4 levels)
- ✅ GDPR-compliant consent mechanism
- ✅ Session management

### Navigation System
- ✅ Shortest path calculation (Dijkstra's algorithm)
- ✅ Alternative route suggestions
- ✅ Accessibility-aware routing (wheelchair/lift)
- ✅ Lift status monitoring
- ✅ Text-based directions

### Notifications
- ✅ User-specific notifications
- ✅ Delivery status tracking
- ✅ Broadcast messaging (admin)

### Analytics Dashboard (Admin Only)
- ✅ User statistics by role
- ✅ Popular routes and locations
- ✅ Peak usage times
- ✅ Accessibility statistics
- ✅ Interactive Plotly charts
- ✅ Static Matplotlib reports

### Logging & Compliance
- ✅ Activity logs (user actions)
- ✅ Alert logs (notifications)
- ✅ Audit logs (admin changes)
- ✅ Timestamped records

---

## 📁 Project Structure

```
scns_flask_project/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── auth/                   # Authentication module
│   ├── routes.py           # Login, register, logout
│   ├── mfa.py              # Multi-factor authentication
│   └── permissions.py      # Role-based decorators
│
├── users/                  # User management
│   ├── models.py           # User data model
│   └── services.py         # Admin user operations
│
├── navigation/             # Campus navigation
│   ├── routes.py           # Navigation endpoints
│   ├── pathfinder.py       # Shortest path algorithm
│   └── accessibility.py    # Lift/accessibility checks
│
├── notifications/          # Alert system
│   ├── engine.py           # Notification logic
│   └── logger.py           # Alert logging
│
├── analytics/              # Data analytics
│   ├── metrics.py          # Usage statistics
│   └── visualisations.py   # Chart generation
│
├── dashboard/              # Admin dashboard
│   ├── routes.py           # Dashboard pages
│   └── widgets.py          # UI components
│
├── data/                   # CSV data files
│   ├── scns_users.csv
│   ├── scns_locations.csv
│   ├── scns_routes.csv
│   └── scns_notifications.csv
│
├── templates/              # HTML templates (Jinja2)
├── static/css/             # CSS stylesheets
├── logs/                   # System logs
└── utils/                  # Shared utilities
```

---

## 🛠️ Technologies

- **Framework:** Flask 3.0
- **Charts:** Matplotlib, Plotly
- **Data:** Pandas, CSV
- **Security:** hashlib (SHA256)
- **Frontend:** HTML5, CSS3 (custom dark theme)

---

## 📋 Role Permissions

| Feature | Admin | Faculty | Student | Visitor |
|---------|:-----:|:-------:|:-------:|:-------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Navigation | ✅ | ✅ | ✅ | ✅ |
| Notifications | ✅ | ✅ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Analytics | ✅ | ❌ | ❌ | ❌ |
| Content Mgmt | ✅ | ✅ | ❌ | ❌ |

---

## 📄 License

This project is developed for CPS7002 assessment at St. Mary's University.
