# API Reference Documentation

## Authentication

### Login
- **Endpoint**: `POST /api/auth/login/`
- **Description**: Authenticate user and get access tokens
- **Request Body**:
  ```json
  {
    "usernameOrEmail": "string",
    "password": "string"
  }
  ```
- **Response**:
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
- **Endpoint**: `POST /api/auth/register/`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "firstName": "string",
    "lastName": "string"
  }
  ```
- **Response**: 201 Created
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
- **Endpoint**: `POST /api/auth/password/reset/`
- **Description**: Request password reset email
- **Request Body**: `{ "email": "string" }`
- **Response**: `{ "message": "Password reset email sent" }`

### Token Refresh
- **Endpoint**: `POST /api/auth/token/refresh/`
- **Description**: Get new access token using refresh token
- **Request Body**: `{ "refresh": "string" }`
- **Response**: `{ "access": "string" }`

## User Management

### List Users
- **Endpoint**: `GET /api/users/users/`
- **Access**: Admin, Manager
- **Query Parameters**:
  - `page`: Page number
  - `search`: Search term
  - `role`: Filter by role
  - `department`: Filter by department ID
- **Response**:
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

### User Profile Operations
- **Get Profile**: `GET /api/users/profiles/me/`
- **Update Profile**: `PATCH /api/users/profiles/{id}/`
- **Request Body**:
  ```json
  {
    "phone_number": "string",
    "department": "integer",
    "role": "string"
  }
  ```

### User Activities
- **List Activities**: `GET /api/users/activities/`
- **Query Parameters**:
  - `user_id`: Filter by user
  - `start_date`: Start date
  - `end_date`: End date
- **Response**:
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

## Asset Management

### Assets
- **List Assets**: `GET /api/assets/`
  - Query Parameters:
    - `status`: Filter by status
    - `category`: Filter by category
    - `department`: Filter by department
    - `search`: Search term

- **Create Asset**: `POST /api/assets/`
  - Request Body:
    ```json
    {
      "name": "string",
      "category": "integer",
      "status": "string",
      "department": "integer",
      "purchase_date": "date",
      "value": "decimal",
      "specifications": "object",
      "location": "string"
    }
    ```

- **Update Asset**: `PATCH /api/assets/{id}/`
- **Delete Asset**: `DELETE /api/assets/{id}/`
- **Asset Details**: `GET /api/assets/{id}/`

### Asset Categories
- **List Categories**: `GET /api/categories/`
- **Create Category**: `POST /api/categories/`
- **Update Category**: `PATCH /api/categories/{id}/`
- **Delete Category**: `DELETE /api/categories/{id}/`

## Request Management

### Asset Requests
- **List Requests**: `GET /api/requests/`
  - Query Parameters:
    - `status`: Filter by status
    - `priority`: Filter by priority
    - `type`: Filter by request type

- **Create Request**: `POST /api/requests/`
  - Request Body:
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

- **Approve Request**: `PATCH /api/requests/{id}/approve/`
  - Request Body:
    ```json
    {
      "comments": "string",
      "status": "APPROVED"
    }
    ```

### Request Types
- **List Types**: `GET /api/requests/types/`
- **Create Type**: `POST /api/requests/types/`
- **Update Type**: `PATCH /api/requests/types/{id}/`
- **Delete Type**: `DELETE /api/requests/types/{id}/`

## Report Generation

### Reports
- **List Reports**: `GET /api/reports/`
  - Query Parameters:
    - `type`: Report type
    - `start_date`: Start date
    - `end_date`: End date

- **Generate Report**: `POST /api/reports/`
  - Request Body:
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
- **Dashboard**: `GET /api/reports/metrics/dashboard/`
- **Asset Overview**: `GET /api/reports/metrics/asset-overview/`
- **Department Usage**: `GET /api/reports/metrics/department-usage/`
- **Trends**: `GET /api/reports/metrics/trends/`

## Common Response Codes

### Success Responses
- **200 OK**: Request successful
- **201 Created**: Resource created
- **204 No Content**: Request successful, no content returned

### Error Responses
- **400 Bad Request**:
  ```json
  {
    "error": "string",
    "detail": "Error description"
  }
  ```

- **401 Unauthorized**:
  ```json
  {
    "detail": "Authentication credentials were not provided."
  }
  ```

- **403 Forbidden**:
  ```json
  {
    "detail": "You do not have permission to perform this action."
  }
  ```

- **404 Not Found**:
  ```json
  {
    "detail": "Not found."
  }
  ```

- **500 Server Error**:
  ```json
  {
    "error": "Internal server error",
    "detail": "Error description"
  }
  ```

## Authentication Headers

All authenticated endpoints require:
```http
Authorization: Bearer <access_token>
```

## Rate Limiting

- Anonymous: 100 requests per day
- Authenticated: 1000 requests per day
- Response Headers:
  ```http
  X-RateLimit-Limit: <requests_per_day>
  X-RateLimit-Remaining: <remaining_requests>
  X-RateLimit-Reset: <reset_timestamp>
  ```

## Pagination

All list endpoints support:
- Page-based pagination
- Query parameters:
  - `page`: Page number
  - `page_size`: Items per page (default: 10)
- Response format:
  ```json
  {
    "count": "total_items",
    "next": "next_page_url",
    "previous": "previous_page_url",
    "results": []
  }
  ``` 