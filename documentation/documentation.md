# Asset Management System Documentation

> For detailed project specifications and additional documentation, visit our [Dropbox Paper Documentation](https://www.dropbox.com/scl/fi/ubd4rkfjlokbjciwra2ki/SPH-Asset-Management-System-Backend.paper?rlkey=i6kbfaw21eef3zjvyzhyc063d&st=o2yh2ffb&dl=0)

## Project Overview
This is a Django-based Asset Management System that helps organizations track and manage their assets, with features for asset assignment, categorization, and tracking. For detailed system design and architecture, see [System Design Documentation](system-design.md).

## Project Structure

### Core Configuration (`config/`)
- Main project configuration directory
- Contains settings, URL routing, and WSGI/ASGI configurations
- Key files:
  - `settings.py`: Project-wide settings and configurations
  - `urls.py`: Main URL routing
  - `wsgi.py` & `asgi.py`: Web server configurations

### Applications (`apps/`)
The project is organized into multiple Django applications, each handling specific functionality:

#### 1. Assets (`apps/assets/`)
- Core application for asset management
- Features:
  - Asset creation and management
  - Asset assignment to users and departments
  - Asset categorization and tagging
- Key models:
  - `Asset`: Represents physical or digital assets with properties like name, type, serial number, etc.

#### 2. Authentication (`apps/authentication/`)
- Handles user authentication and authorization
- Set up for JWT-based authentication using `djangorestframework-simplejwt`

#### 3. Users (`apps/users/`)
- User management functionality
- Built on top of Django's default user system

#### 4. Departments (`apps/departments/`)
- Department management
- Allows organization of assets by department

#### 5. Categories (`apps/categories/`)
- Asset categorization system
- Helps in organizing assets by type or purpose

#### 6. Tags (`apps/tags/`)
- Flexible tagging system for assets
- Enables multiple categorization and easier asset searching

#### 7. Reports (`apps/reports/`)
- Reporting functionality
- For generating asset-related reports and analytics

#### 8. Requests (`apps/requests/`)
- Handles asset request management
- For processing asset assignments and transfers

### API Structure
- RESTful API using Django REST Framework
- Default router for automatic URL configuration
- JWT authentication for secure API access
For detailed API endpoints and structure, see [API Documentation](system-design.md#api-endpoints-table).

### Static Files
- Configured in two locations:
  - Global static files: `static/`
  - App-specific static files: `assets/statics/`

### Database
- Currently configured to use SQLite3
- Can be easily modified to use other databases like PostgreSQL
For detailed database schema and relationships, see [Database Schema](system-design.md#database-schema-representation).

## Technical Stack
- Django 5.1.3
- Django REST Framework
- JWT Authentication
- CORS support
- Additional libraries:
  - django-filter
  - python-barcode
  - Pillow (for image processing)
  - python-Levenshtein (for string matching)

## Application Features
1. Asset Management
   - Create, read, update, and delete assets
   - Asset assignment to users and departments
   - Asset status tracking
   - Serial number management

2. User Management
   - User authentication and authorization
   - Role-based access control
   - Department association

3. Categorization
   - Hierarchical category system
   - Flexible tagging system
   - Department organization

4. API Endpoints
   - RESTful API endpoints for all major functionalities
   - Protected routes with JWT authentication
   - Filtering and search capabilities

## Development Setup
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Run development server:
   ```bash
   python manage.py runserver
   ```

## Security Considerations
- JWT-based authentication
- CORS configuration available
- Django's built-in security features
- Password validation rules configured

## Future Enhancements
- Asset maintenance tracking
- Advanced reporting features
- Asset lifecycle management
- Integration with external systems
- Audit logging 