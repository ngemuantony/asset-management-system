# API Endpoints Documentation

## Authentication Endpoints
Base URL: `/api/auth/`

### Login
- **POST** `/login/`
  - Authenticate user and get access token
  - Body:
    ```json
    {
      "usernameOrEmail": "string",
      "password": "string"
    }
    ```
  - Response:
    ```json
    {
      "message": "Login successful",
      "user": {
        "username": "string",
        "email": "string",
        "firstName": "string",
        "lastName": "string",
        "role": "string"
      },
      "tokens": {
        "access": "string",
        "refresh": "string"
      }
    }
    ```

### Register
- **POST** `/register/`
  - Register a new user
  - Body:
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string",
      "firstName": "string",
      "lastName": "string"
    }
    ```
  - Response:
    ```json
    {
      "message": "Registration successful",
      "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
      }
    }
    ```

### Password Reset
- **POST** `/password/reset/`
  - Request password reset email
  - Body: `{ "email": "string" }`
  - Response: `{ "message": "Password reset email sent" }`

- **POST** `/password/reset/confirm/{token}/`
  - Confirm password reset
  - Body: `{ "password": "string" }`
  - Response: `{ "message": "Password reset successful" }`

### Token
- **POST** `/token/refresh/`
  - Refresh access token
  - Body: `{ "refresh": "string" }`
  - Response: `{ "access": "string" }`

## User Management Endpoints
Base URL: `/api/users/`

### Users
- **GET** `/users/`
  - List all users (admin/manager only)
  - Query Parameters:
    - `page`: Page number
    - `search`: Search term
    - `role`: Filter by role
    - `department`: Filter by department ID
  - Response:
    ```json
    {
      "count": "integer",
      "next": "string",
      "previous": "string",
      "results": [
        {
          "id": "integer",
          "username": "string",
          "email": "string",
          "firstName": "string",
          "lastName": "string",
          "is_active": "boolean"
        }
      ]
    }
    ```

### User Profiles
- **GET** `/profiles/me/`
  - Get current user's profile
  - Response:
    ```json
    {
      "id": "integer",
      "user": {
        "username": "string",
        "email": "string"
      },
      "role": "string",
      "department": "integer",
      "employee_id": "string",
      "phone_number": "string",
      "status": "string"
    }
    ```

- **PATCH** `/profiles/{id}/`
  - Update user profile
  - Body:
    ```json
    {
      "phone_number": "string",
      "department": "integer",
      "role": "string"
    }
    ```

### User Activities
- **GET** `/activities/`
  - List user activities (admin/manager only)
  - Query Parameters:
    - `user_id`: Filter by user
    - `start_date`: Start date
    - `end_date`: End date
  - Response:
    ```json
    {
      "count": "integer",
      "results": [
        {
          "id": "integer",
          "username": "string",
          "action": "string",
          "timestamp": "datetime",
          "details": "object"
        }
      ]
    }
    ```

## Asset Management Endpoints
Base URL: `/api/assets/`

### Assets
- **GET** `/`
  - List all assets
  - Query Parameters:
    - `status`: Filter by status
    - `category`: Filter by category
    - `department`: Filter by department
    - `search`: Search term

- **POST** `/`
  - Create new asset (admin only)
  - Body:
    ```json
    {
      "name": "string",
      "category": "integer",
      "status": "string",
      "department": "integer",
      "purchase_date": "date",
      "value": "decimal"
    }
    ```

### Asset Categories
Base URL: `/api/categories/`

- **GET** `/`
  - List all categories
- **POST** `/`
  - Create category (admin only)
- **PATCH** `/{id}/`
  - Update category
- **DELETE** `/{id}/`
  - Delete category (admin only)

## Request Management
Base URL: `/api/requests/`

### Asset Requests
- **GET** `/`
  - List requests
  - Query Parameters:
    - `status`: Filter by status
    - `priority`: Filter by priority
    - `type`: Filter by request type

- **POST** `/`
  - Create request
  - Body:
    ```json
    {
      "request_type": "integer",
      "asset": "integer",
      "title": "string",
      "description": "string",
      "priority": "string",
      "desired_date": "date"
    }
    ```

- **PATCH** `/{id}/approve/`
  - Approve request
  - Body:
    ```json
    {
      "comments": "string",
      "status": "APPROVED"
    }
    ```

## Report Generation
Base URL: `/api/reports/`

### Reports
- **GET** `/`
  - List reports
  - Query Parameters:
    - `type`: Report type
    - `start_date`: Start date
    - `end_date`: End date

- **POST** `/`
  - Generate report
  - Body:
    ```json
    {
      "report_type": "string",
      "parameters": {
        "start_date": "date",
        "end_date": "date",
        "format": "string"
      }
    }
    ```

### Metrics
- **GET** `/metrics/dashboard/`
  - Get dashboard metrics
- **GET** `/metrics/asset-overview/`
  - Get asset metrics
- **GET** `/metrics/department-usage/`
  - Get department metrics
- **GET** `/metrics/trends/`
  - Get trending metrics

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "error": "string",
  "detail": "Error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Server Error
```json
{
  "error": "Internal server error",
  "detail": "Error description"
}
``` 