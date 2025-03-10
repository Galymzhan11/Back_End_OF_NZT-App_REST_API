# 🚀 NZT App Back-End – REST API

## 📌 Overview
This project is a **Django-based REST API** designed to manage **user authentication, profiles, and payments**. It provides a secure and scalable backend for the **NZT App** with features such as:
- **JWT authentication**
- **Profile management**
- **Payment processing via YooKassa**

## 🛠️ Technologies Used
This API is built using modern backend technologies, ensuring **stability, security, and scalability**:

- **Programming Language**: Python
- **Framework**: Django + Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Payments Integration**: YooKassa
- **API Documentation**: Swagger / Postman
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

---

## 📂 Project Structure
```
📁 Back_End_OF_NZT-App_REST_API
├── 📁 users/         # User management & JWT authentication
├── 📁 profiles/      # User profile management
├── 📁 payments/      # Payment processing (YooKassa)
├── 📁 config/        # Project settings
├── 📁 static/        # Static files
├── 📁 templates/     # Email templates
├── 📄 requirements.txt  # Project dependencies
├── 📄 Dockerfile        # Containerization setup
├── 📄 .env.example      # Environment variables example
├── 📄 README.md         # Project documentation
```

---

## 🚀 Setup & Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/Galymzhan11/Back_End_OF_NZT-App_REST_API.git
cd Back_End_OF_NZT-App_REST_API
```

### 2️⃣ Set Up Environment Variables
Create a **.env** file in the root directory and add the following:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 3️⃣ Run with Docker
```sh
docker-compose up --build
```

### 4️⃣ Run Locally (Without Docker)
```sh
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📌 API Endpoints

### 🧑‍💻 1. User Management
| Method | URL | Description |
|--------|-----|-------------|
| **POST** | `/api/users/register/` | User registration |
| **POST** | `/api/users/register/verify/` | Email verification |

### 🔐 JWT Authentication
| Method | URL | Description |
|--------|-----|-------------|
| **POST** | `/api/users/token/` | Get JWT access token |
| **POST** | `/api/users/token/refresh/` | Refresh JWT token |
| **POST** | `/api/users/token/verify/` | Verify JWT token |
| **POST** | `/api/users/logout/` | Logout (invalidate tokens) |

### 🔑 Password Reset
| Method | URL | Description |
|--------|-----|-------------|
| **POST** | `/api/users/password/reset/` | Request password reset |
| **POST** | `/api/users/password/reset/verify/` | Verify reset token |
| **POST** | `/api/users/password/reset/confirm/` | Confirm new password |

### 🏆 2. User Profiles
| Method | URL | Description |
|--------|-----|-------------|
| **GET** | `/api/profiles/profile/` | Get user profile |
| **PUT** | `/api/profiles/profile/edit/` | Edit user profile |
| **GET** | `/api/profiles/user-ranking/` | Get user ranking |

### 💰 3. Payment Processing (YooKassa)
| Method | URL | Description |
|--------|-----|-------------|
| **POST** | `/api/payments/create-payment/` | Create a payment (subject_id, description) |
| **POST** | `/api/payments/yookassa-webhook/` | YooKassa webhook |

---

## 🖥️ Code Implementation

### 1️⃣ JWT Authentication Setup
This project uses **Simple JWT** for secure authentication. Example setup in `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```
When a user logs in, they receive an **access token** and **refresh token**, which can be used for authenticated requests.

### 2️⃣ User Registration & Email Verification

#### 📌 Registration Endpoint (`/api/users/register/`)
```python
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
```

#### 📌 Email Verification (`/api/users/register/verify/`)
```python
class VerifyEmailView(APIView):
    def post(self, request):
        token = request.data.get('token')
        user = get_object_or_404(User, verification_token=token)
        user.is_verified = True
        user.save()
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
```

### 3️⃣ Payment Processing with YooKassa

#### 📌 Creating a Payment (`/api/payments/create-payment/`)
```python
class CreatePaymentView(APIView):
    def post(self, request):
        subject_id = request.data.get('subject_id')
        amount = request.data.get('amount')

        payment = Payment.objects.create(
            subject_id=subject_id,
            amount=amount,
            status="pending"
        )

        return Response({"payment_id": payment.id}, status=status.HTTP_201_CREATED)
```

#### 📌 Handling YooKassa Webhooks (`/api/payments/yookassa-webhook/`)
```python
class YooKassaWebhookView(APIView):
    def post(self, request):
        event = request.data
        payment_id = event.get('object', {}).get('id')
        payment_status = event.get('object', {}).get('status')

        payment = get_object_or_404(Payment, id=payment_id)
        payment.status = payment_status
        payment.save()

        return Response({"message": "Webhook received"}, status=status.HTTP_200_OK)
```

---

## 🔐 Security Features
This API includes modern security mechanisms:
✔ **JWT Authentication**
✔ **Password Hashing** (bcrypt, Argon2)
✔ **CORS Protection**
✔ **Rate Limiting** to Prevent DDoS Attacks

---

## 🚀 Deployment & CI/CD
✅ **GitHub Actions** – Runs automated tests before deployment.
✅ **Docker + Kubernetes** – For production deployment.

Deploy using Kubernetes:
```sh
kubectl apply -f k8s/
```

📄 **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌟 How to Contribute?
💡 **Fork this repository** and submit a pull request!
⭐ **Star this repo** if you find it useful.
🐛 **Report Issues** if you find any bugs.

---

🚀 **Happy Coding!**