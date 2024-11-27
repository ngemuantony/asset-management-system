# SPH Asset Management System Architecture

## System Overview

The SPH Asset Management System is a Django-based REST API that provides comprehensive asset management functionality with role-based access control.

## Core Components

### 1. Authentication Module (`apps.authentication`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/auth/login/` | POST | User authentication | Public |
| `/api/auth/register/` | POST | User registration | Public |
| `/api/auth/logout/` | POST | User logout | Authenticated |
| `/api/auth/password/reset/` | POST | Request password reset | Public |
| `/api/auth/password/reset/confirm/{token}/` | POST | Confirm password reset | Public |

### 2. User Management Module (`apps.users`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/users/users/` | GET | List users | Admin/Manager |
| `/api/users/users/` | POST | Create user | Admin |
| `/api/users/users/{id}/` | GET | Get user details | Admin/Manager/Owner |
| `/api/users/users/{id}/` | PATCH/PUT | Update user | Admin/Manager/Owner |
| `/api/users/users/me/` | GET | Get current user | Authenticated |
| `/api/users/profiles/` | GET | List profiles | Admin/Manager |
| `/api/users/profiles/{id}/` | GET | Get profile details | Admin/Manager/Owner |
| `/api/users/profiles/{id}/` | PATCH | Update profile | Admin/Manager/Owner |
| `/api/users/activities/` | GET | List user activities | Admin/Manager |
| `/api/users/activities/statistics/` | GET | Get activity stats | Admin/Manager |

### 3. Asset Management Module (`apps.assets`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/assets/` | GET | List assets | Authenticated |
| `/api/assets/` | POST | Create asset | Admin |
| `/api/assets/{id}/` | GET | Get asset details | Authenticated |
| `/api/assets/{id}/` | PATCH/PUT | Update asset | Admin/Manager |
| `/api/assets/{id}/` | DELETE | Delete asset | Admin |
| `/api/assets/{id}/maintenance/` | POST | Record maintenance | Admin/Manager |
| `/api/assets/{id}/assign/` | POST | Assign asset | Admin/Manager |

### 4. Request Management Module (`apps.requests`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/requests/` | GET | List requests | Authenticated |
| `/api/requests/` | POST | Create request | Authenticated |
| `/api/requests/{id}/` | GET | Get request details | Requester/Approver |
| `/api/requests/{id}/approve/` | POST | Approve request | Admin/Manager |
| `/api/requests/{id}/reject/` | POST | Reject request | Admin/Manager |
| `/api/requests/types/` | GET | List request types | Authenticated |

### 5. Reports Module (`apps.reports`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/reports/` | GET | List reports | Admin/Manager |
| `/api/reports/` | POST | Generate report | Admin/Manager |
| `/api/reports/metrics/dashboard/` | GET | Dashboard metrics | Admin/Manager |
| `/api/reports/metrics/asset-overview/` | GET | Asset metrics | Admin/Manager |
| `/api/reports/metrics/department-usage/` | GET | Department metrics | Admin/Manager |
| `/api/reports/metrics/trends/` | GET | Trending metrics | Admin/Manager |

### 6. Categories and Tags (`apps.categories`, `apps.tags`)
| Endpoint | Method | Description | Access |
|----------|---------|-------------|---------|
| `/api/categories/` | GET | List categories | Authenticated |
| `/api/categories/` | POST | Create category | Admin |
| `/api/tags/` | GET | List tags | Authenticated |
| `/api/tags/` | POST | Create tag | Admin |

## Role-Based Access Control

### User Roles
1. **Admin**
   - Full system access
   - Can manage users and roles
   - Can approve/reject any request
   - Can manage all assets

2. **Manager**
   - Department-level access
   - Can manage department users
   - Can approve department requests
   - Can manage department assets

3. **User**
   - Can view assigned assets
   - Can create requests
   - Can view own profile
   - Limited report access

## Technical Stack

### Backend
- Django 5.1.3
- Django REST Framework
- JWT Authentication
- SQLite Database (Development)
- File Storage for Assets

### Security Features
- JWT Token Authentication
- Role-Based Access Control
- Request Rate Limiting
- CORS Configuration
- Password Validation Rules

### Monitoring & Logging
- User Activity Logging
- Request Tracking
- Performance Metrics
- Error Logging

### API Documentation
- Swagger/OpenAPI Documentation
- Available at `/swagger/` and `/redoc/`
- Interactive API Testing Interface

## Data Models

### Core Models
- CustomUser
- UserProfile
- UserActivityLog
- Department

### Asset Models
- Asset
- AssetCategory
- AssetMaintenance
- AssetAssignment
- Tag

### Request Models
- AssetRequest
- RequestType
- RequestApproval

### Report Models
- Report
- ReportTemplate
- Metrics

## Caching Strategy
- User Session Caching
- Token Caching
- Query Result Caching
- File Caching

## File Storage
- Asset Documents
- Request Attachments
- Report Files
- User Uploads

## Error Handling
- Custom Exception Classes
- Standardized Error Responses
- Validation Error Handling
- Permission Error Handling

## Monitoring & Metrics
- User Activity Tracking
- Request Success/Failure Rates
- Response Times
- Resource Usage
