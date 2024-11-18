Here is a refined Markdown documentation of your Vehicle Information API along with an explanation of how API Key creation is implemented:

---

# Vehicle Information API Documentation

## Overview
A comprehensive API for secure vehicle information services with API key management, rate limiting, and usage tracking for both internal and external integrations.

---

## Features
- Multiple authentication methods: **JWT, API Keys**
- Role-based access control for added security
- **API Key Management System** for creating and managing keys
- **Rate Limiting** and tier-based usage plans
- Comprehensive **Error Handling**
- Usage tracking and analytics

---

## Base URL
```
http://your-domain.com/api/v1
```

---

## Authentication Methods

### 1. JWT Authentication (For internal apps)
Add the header:  
```
Authorization: Bearer [JWT_TOKEN]
```

### 2. API Key Authentication (For external integration)
Add the header:  
```
X-API-Key: YOUR_API_KEY
```

---

## Available Plans
| Plan       | Daily Limit | Rate Limit         | Max Keys |
|------------|-------------|--------------------|----------|
| Free       | 1,000       | 100/minute         | 2        |
| Basic      | 5,000       | 200/minute         | 5        |
| Premium    | 20,000      | 600/minute         | 10       |
| Enterprise | 100,000     | 1 request/second   | 20       |

---

## Endpoints

### Authentication Endpoints

#### 1. User Signup
```http
POST /auth/signup
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secure_password"
}
```

#### 2. User Login
```http
POST /auth/login
Content-Type: application/json

{
    "username": "johndoe",
    "password": "secure_password"
}
```

---

### API Key Management Endpoints

#### 1. Create API Key
```http
POST /keys/create
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "name": "My API Key",
    "plan": "free"
}
```

#### 2. List API Keys
```http
GET /keys
Authorization: Bearer YOUR_JWT_TOKEN
```

#### 3. Revoke API Key
```http
POST /keys/revoke
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "api_key": "YOUR_API_KEY"
}
```

---

## Vehicle Information Endpoints

### 1. Get Vehicle Details (JWT Auth)
```http
POST /vehicles/data
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "veh_num": "DL8CX5463"
}
```

### 2. Get Vehicle Details (API Key)
```http
POST /vehicles/api/lookup
X-API-Key: YOUR_API_KEY
Content-Type: application/json

{
    "veh_num": "DL8CX5463"
}
```

---

## Error Handling

### Common Error Codes
| Status Code | Description                   |
|-------------|-------------------------------|
| 400         | Bad Request                  |
| 401         | Unauthorized                 |
| 403         | Forbidden                    |
| 429         | Rate Limit Exceeded          |
| 500         | Internal Server Error        |

### Error Response Format
```json
{
    "status": "error",
    "message": "Error description",
    "error_code": "ERROR_CODE"
}
```

---

## Explanation: API Key Creation Implementation

1. **Key Generation**  
   - When an authenticated user requests an API key, the system generates a unique key in the format:  
     ```
     veh_[32-character-hex]
     ```
   - This key is tied to the user account and the selected plan.

2. **Key Storage**  
   - Each key is stored securely in the database with metadata like:
     - User ID
     - Plan type (e.g., Free, Premium)
     - Rate limits
     - Creation timestamp
   - Example schema for MongoDB:
     ```json
     {
         "user_id": "user123",
         "api_key": "veh_abc123xyz456...",
         "plan": "premium",
         "rate_limit": 600,
         "created_at": "2024-11-19T10:00:00Z",
         "status": "active"
     }
     ```

3. **Validation during Requests**  
   - Every API request with an API key undergoes validation:
     - Check if the key exists.
     - Verify that it’s active and not revoked.
     - Ensure the request is within the user’s rate and daily limits.

4. **Rate Limiting**  
   - A rate-limiting mechanism checks the usage of the key in real-time.
   - If limits are exceeded, the request returns a `429: Rate Limit Exceeded` error.

5. **Implementation Code**  
   - Key generation using Python (example):
     ```python
     import secrets

     def generate_api_key():
         return f"veh_{secrets.token_hex(16)}"

     # Example usage
     new_key = generate_api_key()
     print(new_key)  # Output: veh_5f2b1e7c2b8d9a12c3f1...
     ```

   - Key creation endpoint logic:
     ```python
     @app.route('/keys/create', methods=['POST'])
     @token_required  # JWT authentication required
     def create_key():
         data = request.json
         user_id = get_current_user_id()  # Extract user ID from token
         new_key = generate_api_key()
         plan = data.get('plan', 'free')

         # Save key to database
         db.keys.insert_one({
             "user_id": user_id,
             "api_key": new_key,
             "plan": plan,
             "created_at": datetime.utcnow(),
             "status": "active"
         })

         return jsonify({"api_key": new_key}), 201
     ```

This implementation ensures secure generation, management, and validation of API keys.
