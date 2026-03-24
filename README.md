# 🛡️ Hunter BOT License Server

This repository contains the backend server for the Hunter BOT license verification system.

## 🚀 Quick Deployment (Render)

1.  **Create a New Web Service** on Render.
2.  **Connect this Repository**.
3.  **Environment Settings**:
    *   **Runtime**: Python
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn server:app --host 0.0.0.0 --port 10000`
4.  **Environment Variables**:
    *   Add `MONGODB_URI` with your MongoDB Atlas connection string.

## 📁 File Structure
*   `server.py`: The FastAPI application for license verification.
*   `requirements.txt`: Necessary libraries for deployment.

## 🔐 Security Note
Validation logic, expiry checks, and device binding are all handled server-side to prevent bypasses.
