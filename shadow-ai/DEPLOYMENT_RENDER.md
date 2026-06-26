# Deploying Shadow AI to Render

Shadow AI consists of a FastAPI backend and a static HTML/JS/CSS frontend. Since the application already includes a `Dockerfile` that packages both the backend and frontend together, the **Docker runtime** is the recommended, most reliable, and easiest way to deploy it to Render.

This guide provides a comprehensive step-by-step walkthrough to get your application live.

---

## Prerequisites

1. A **GitHub** account with your Shadow AI repository pushed.
2. A **Render** account (sign up at [render.com](https://render.com)).
3. API keys for any external services your app uses (such as OpenAI, Groq, RapidAPI, etc.).

---

## Step 1: Ensure Your Code is Pushed to GitHub
Render deploys your code by connecting to your GitHub repository. Make sure your local changes are committed and pushed to your remote repository:
```bash
git add .
git commit -m "Configure deployment scripts"
git push origin main
```

---

## Step 2: Create a New Web Service on Render
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click the **New +** button in the top right corner and select **Web Service**.
3. Select **Build and deploy from a Git repository**, then click **Next**.
4. Find and select your **shadow-ai** repository from the list. (If you don't see it, make sure Render has permission to access your GitHub repositories or connect your GitHub account).

---

## Step 3: Configure the Web Service Settings
Fill in the deployment details in the configuration page:

*   **Name**: Choose a unique name for your application (e.g., `shadow-ai-app`).
*   **Region**: Choose the region closest to you or your target users (e.g., `Oregon (US West)` or `Frankfurt (EU Central)`).
*   **Branch**: Select your default branch (usually `main`).
*   **Runtime**: Select **Docker** (Very Important!).
*   **Instance Type**: Choose **Free** (or a paid instance if you need more resources/no spin-downs).

---

## Step 4: Configure Advanced Build Settings
Scroll down to the bottom of the page and click **Advanced** to open more options. Set the following build configuration:

*   **Docker Build Context**: `.` (Keep as dot. This tells Render to run the build from the project root directory).
*   **Dockerfile Path**: `backend/Dockerfile` (Tells Render where the Dockerfile is located since it's not in the root directory).

---

## Step 5: Configure Environment Variables
In the **Environment Variables** section of the Render dashboard, add the variables your application requires. 

| Key | Value / Example | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:////data/shadow_ai.db` | Connects SQLite database inside the persistent volume. |
| `SECRET_KEY` | `your-super-long-secure-jwt-signing-key` | Used for JWT security signing (generate a secure random string). |
| `GROQ_API_KEY` | `gsk_...` | Groq API Key (if using Groq LLM). |
| `RAPID_API_KEY` | `your-rapidapi-key` | Rapid API Key (if using search tools). |
| `IMAGE_GEN_API_KEY` | `your-google-image-gen-key` | Google API key used for image generation (if active). |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API Key (if using OpenAI LLMs). |
| `GEMINI_API_KEY` | `AIzaSy...` | Gemini API Key (if using Gemini LLMs). |

> [!TIP]
> You can also copy your local `.env` variables and paste them using the **Secret Files** feature on Render, or add them manually as individual key-value pairs.

---

## Step 6: Configure Persistent Disk (Crucial for SQLite)
Because SQLite uses local file storage, and Render containers have an ephemeral filesystem (data resets on every deploy or restart), **you must add a persistent volume to keep your database intact.**

1. In the **Disks** section (under the Advanced options), click **Add Disk**.
2. Configure the persistent volume:
    *   **Name**: `shadow-db-disk`
    *   **Mount Path**: `/data` (Must match the directory in `DATABASE_URL` and Dockerfile volume).
    *   **Size**: `1 GB` (This is the minimum size, which is more than enough for sqlite database storage).

---

## Step 7: Deploy Your Application
1. Click **Create Web Service** at the bottom of the page.
2. Render will spin up a build container, pull your code from GitHub, build the Docker image using `backend/Dockerfile`, mount your persistent disk, and deploy the service.
3. You can monitor the progress in the **Logs** tab of your Render service page.

---

## Step 8: Access Your Live Application
Once the build completes successfully and the service is marked as **Live**:
*   Render will provide a default URL at the top of your service page (e.g., `https://shadow-ai-app.onrender.com`).
*   Open the app in your browser using the `/ui` route:
    *   **UI Dashboard**: `https://shadow-ai-app.onrender.com/ui`
    *   **Interactive API Docs (Swagger)**: `https://shadow-ai-app.onrender.com/docs`

---

## Troubleshooting & Tips

### 1. Database Connection Errors
If you see errors related to database initialization, make sure:
- The `DATABASE_URL` matches `sqlite+aiosqlite:////data/shadow_ai.db` (note the **four** forward slashes for absolute container path `/data/shadow_ai.db`).
- The persistent disk is mounted exactly at `/data`.

### 2. Slow Startup / Free Tier Sleep
If you are on the Render **Free Tier**:
- The web service will automatically go to sleep after 15 minutes of inactivity.
- The next request to the `/ui` page might take 50-90 seconds to wake up the server. This is normal behavior for Render Free Tier.

### 3. Updating the Deployment
Every time you push a commit to your GitHub `main` branch, Render will automatically trigger a new build and redeploy. You do not need to repeat the steps above.
