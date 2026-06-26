# Shadow AI

Shadow AI is an application consisting of a **FastAPI backend** and a **Vanilla JS/CSS/HTML frontend**. The backend serves the frontend files statically, making it a single unified container deployment.

---

## Getting Started

### Local Development Setup

To run the application locally without Docker:

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory by copying `.env.example` and filling in your values:
   ```bash
   cp .env.example .env
   ```

4. **Run the server**:
   ```bash
   python main.py
   ```
   Or run the provided startup script:
   - On Windows: `start_server.bat`

5. **Access the application**:
   - **UI Dashboard**: `http://localhost:8000/ui`
   - **API Swagger Docs**: `http://localhost:8000/docs`

---

## Deployment Guide

### 1. Environment Variables

Ensure you configure the following environment variables on your server or container platform:

| Variable Name | Description | Default / Example Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy async connection string. | `sqlite+aiosqlite:///./shadow_ai.db` |
| `SECRET_KEY` | Secret key for JWT auth/token signing. | `some-random-long-secure-key` |
| `OPENAI_API_KEY` | OpenAI API key for AI features. | `sk-proj-...` |
| `PORT` | The port the container will bind to. | `8080` |

---

### 2. Docker Deployment (Recommended)

The project includes a `Dockerfile` located at `backend/Dockerfile`.

> [!IMPORTANT]
> **Build Context Rule**: Because the Dockerfile copies files from both `backend/` and `frontend/`, **you must run the docker build command from the root directory of the repository**, referencing the Dockerfile with `-f backend/Dockerfile`.

#### Build the Image
From the **root directory** of your project (where `backend/` and `frontend/` folders live), run:
```bash
docker build -t shadow-ai -f backend/Dockerfile .
```

#### Run the Container Locally
You can run the container locally to verify:
```bash
docker run -d -p 8080:8080 \
  -e SECRET_KEY="your-super-secret-key" \
  -e OPENAI_API_KEY="your-openai-api-key" \
  shadow-ai
```
Once started, you can access the application at:
- **UI Dashboard**: `http://localhost:8080/ui`
- **API Swagger Docs**: `http://localhost:8080/docs`

---

### 3. Deploying to Cloud Platforms

#### Option A: Railway (Easiest)
1. Sign in to [Railway.app](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `shadow-ai` repository.
4. Railway will automatically detect the `backend/Dockerfile`. Verify your build settings:
   - **Root Directory**: `/` (default).
   - **Dockerfile Path**: `backend/Dockerfile`.
5. Go to the **Variables** tab and add your secrets (`SECRET_KEY`, `OPENAI_API_KEY`).
6. Click **Deploy**.

#### Option B: Render
1. Sign in to [Render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Configure the service settings:
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Build Context**: `.` (Keep as root directory)
5. Add your environment variables under the **Env Groups / Environment** section.
6. Click **Create Web Service**.

#### Option C: Google Cloud Run
1. **Configure Google Cloud SDK** and log in:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. **Build and Submit** the image using Cloud Build:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/shadow-ai --file backend/Dockerfile .
   ```
3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy shadow-ai \
     --image gcr.io/YOUR_PROJECT_ID/shadow-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --set-env-vars="SECRET_KEY=your-secret-key,OPENAI_API_KEY=your-openai-key"
   ```

---

### 4. Persistent Databases
If you use SQLite and deploy to standard cloud host providers, data will reset on every server restart. To keep your database persistent:
1. Create a persistent volume (e.g. at `/data`).
2. Set your environment variable: `DATABASE_URL=sqlite+aiosqlite:////data/shadow_ai.db`.
3. In your cloud provider dashboard, map `/data` to that persistent directory volume.
