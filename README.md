# Kadambini Server
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/anurag6569201/KadambiniServer)

Kadambini Server is the backend for **Arogya Kadambini**, a sophisticated health and wellness platform that combines ancestral wisdom with modern AI. Built with Django and Django REST Framework, it serves as the central hub for managing user data, family health histories, and generating powerful, AI-driven health insights. The platform leverages the Google Gemini API to transform structured family tree data into actionable wellness plans, identify hereditary risks, and provide a conversational health assistant.

## Key Features

*   **AI-Powered Family Tree:** Generate and modify intricate family trees using natural language prompts. The system intelligently parses instructions to create and update member nodes and relationships.
*   **Comprehensive Health Insights:** The `analysis` module provides a suite of AI-driven reports:
    *   **Generational Insights:** Uncover health patterns passed down through generations.
    *   **Hereditary Risk Analysis:** Identify high, moderate, and low-risk conditions based on family medical history.
    *   **Offspring Risk Insights:** Predict potential health traits and risks for future children.
    *   **Smart Health Pathways:** Receive personalized, actionable recommendations for managing health.
    *   **Health Will & Wisdom:** Distill cross-generational health lessons into a shareable legacy.
*   **Family Health Guardian:** An empathetic AI chatbot that answers health-related questions based on the user's family data, providing safe, non-diagnostic guidance.
*   **Secure User Management:** Robust user authentication and profile management using JWT for secure API access.
*   **Custom Admin Interface:** A user-friendly admin dashboard powered by `django-jazzmin` for easy management.

## Tech Stack

*   **Backend:** Django, Django REST Framework
*   **AI:** Google Gemini (`google-generativeai`)
*   **Authentication:** Simple JWT (`djangorestframework-simplejwt`)
*   **Data Validation:** Pydantic
*   **Database:** SQLite3
*   **API Server:** Gunicorn
*   **Admin UI:** Django Jazzmin

## API Endpoints

### Authentication (`/api/auth/`)
| Method | Endpoint         | Description                                     |
|--------|------------------|-------------------------------------------------|
| `POST` | `/register/`     | Creates a new user account.                     |
| `POST` | `/login/`        | Authenticates a user and returns JWT tokens.    |
| `GET`  | `/user/`         | Retrieves profile information for the logged-in user. |
| `POST` | `/logout/`       | Blacklists the user's refresh token.            |

### Family Tree (`/api/maintree/`)
| Method | Endpoint       | Description                                                 |
|--------|----------------|-------------------------------------------------------------|
| `GET`  | `/data/`       | Retrieves the authenticated user's family tree data.        |
| `POST` | `/data/`       | Creates or updates the user's family tree data.             |
| `POST` | `/generate/`   | Generates a new family tree from a natural language prompt. |
| `POST` | `/modify/`     | Modifies an existing tree based on a natural language prompt. |

### Health Analysis (`/api/analysis/`)
| Method | Endpoint                       | Description                                                     |
|--------|--------------------------------|-----------------------------------------------------------------|
| `GET`  | `/generate-insights/`          | Generates and returns multi-sentence generational health insights. |
| `GET`  | `/generate-hereditary-insights/` | Analyzes and returns hereditary risks (high, moderate, low).     |
| `GET`  | `/generate-offspring/`         | Predicts potential health risks and traits for offspring.       |
| `GET`  | `/generate-pathways/`          | Creates personalized "Smart Health Pathways" for each family member. |
| `GET`  | `/generate-health-wisdom/`     | Distills legacy health insights and wisdom from family history. |
| `POST` | `/guardian-chat/`              | Initiates or continues a conversation with the AI Health Guardian. |

## Local Setup and Installation

Follow these steps to get the project running on your local machine.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/anurag6569201/KadambiniServer.git
    cd KadambiniServer
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    python -m venv venv
    
    # On Windows
    venv\Scripts\activate
    
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the project's root directory. Add the following variables with your credentials.

    ```env
    # .env
    DJANGO_SECRET_KEY='your-strong-django-secret-key'
    GEMINI_API_KEY='your-google-gemini-api-key'
    DJANGO_DEBUG=True
    DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
    ```

5.  **Run Database Migrations**
    This command will set up the initial database schema.
    ```bash
    python manage.py migrate
    ```

6.  **Run the Development Server**
    The server will start, typically at `http://127.0.0.1:8000/`.
    ```bash
    python manage.py runserver
    ```

7.  **(Optional) Create-a-Superuser**
    To access the admin panel at `/admin/`, you need-a-superuser account.
    ```bash
    python manage.py createsuperuser
