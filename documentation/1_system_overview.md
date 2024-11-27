# SPH Asset Management System - Technical Documentation

## System Overview

The SPH Asset Management System is a Django-based REST API that provides comprehensive asset management functionality with role-based access control. The system is designed to handle asset tracking, requests, maintenance, and reporting.

### Core Features

1. **User Management**
   - Role-based access control (Admin, Manager, User)
   - User profiles with department assignments
   - Activity logging and monitoring
   - JWT-based authentication

2. **Asset Management**
   - Asset tracking and categorization
   - Asset lifecycle management
   - QR code generation for assets
   - Asset maintenance scheduling

3. **Request Management**
   - Asset request workflow
   - Multi-level approval process
   - Request tracking and status updates
   - File attachment support

4. **Reporting System**
   - Customizable report templates
   - Scheduled report generation
   - Multiple export formats (PDF, Excel, CSV)
   - Analytics and metrics

### Technical Stack

1. **Backend Framework**
   - Django 5.1.3
   - Django REST Framework
   - JWT Authentication
   - SQLite Database (Development)

2. **Key Dependencies**
   - rest_framework_simplejwt
   - drf_yasg (API Documentation)
   - corsheaders (CORS Support)

3. **Development Tools**
   - Swagger/OpenAPI Documentation
   - Django Debug Toolbar
   - Django Extensions

4. **Security Features**
   - JWT Token Authentication
   - Role-Based Access Control
   - Request Rate Limiting
   - CORS Configuration 