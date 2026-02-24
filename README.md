# URL Shortener API

A FastAPI backend for a URL shortener with bookmarking features, Google OAuth, and SQLite storage.

## Local Setup

1. **Clone and Install Dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy `.env.example` to `.env` and fill in the required values:

   ```bash
   cp .env.example .env
   ```

   _Note: Set your `GOOGLE_CLIENT_ID` for OAuth._

3. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. You can visit `http://localhost:8000/docs` for the Swagger UI.

## Render Deployment

This project includes a `render.yaml` blueprint for easy deployment to [Render](https://render.com).

1. Push this repository to GitHub/GitLab.
2. In the Render Dashboard, go to **Blueprints** and click **New Blueprint Instance**.
3. Connect your repository.
4. Render will automatically configure the Web Service with a persistent disk for the SQLite database.
5. Provide the required Environment Variables (`FRONTEND_URL`, `GOOGLE_CLIENT_ID`) in the Render Dashboard when prompted. `JWT_SECRET_KEY` is generated automatically.
