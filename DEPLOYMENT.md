# Deployment Guide for Contract Analyzer

## Issue: 502 Error on Streamlit Cloud

The application consists of two services:
- **Frontend**: Streamlit UI (contract-risk-analyzer-*.streamlit.app)
- **Backend**: FastAPI server (must be deployed separately)

Streamlit Cloud only hosts the frontend, so you need to deploy the backend separately for the app to work.

## Option 1: Deploy with Docker (Recommended for Development)

### Using Docker Compose locally:
```bash
cd contract-analyzer
docker-compose up
```

Visit `http://localhost:8501` for the frontend.

### Using Docker on a VPS/Server:
```bash
# Pull the code
git clone https://github.com/HadiaAkbar/Contract-Risk-analyzer.git
cd Contract-Risk-analyzer/contract-analyzer

# Start services
docker-compose up -d
```

## Option 2: Deploy Backend to Render.com (Free)

1. **Create Render account**: https://render.com

2. **Create New Web Service**:
   - Repository: https://github.com/HadiaAkbar/Contract-Risk-analyzer
   - Root Directory: `contract-analyzer`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Environment: Python 3.11
   - Plan: Free

3. **Set Environment Variables** (Optional):
   - Add any needed environment variables in Render dashboard

4. **Get API URL**:
   - Copy the service URL from Render (e.g., `https://contract-analyzer-api.render.com`)

5. **Update Streamlit Secrets**:
   - Go to https://share.streamlit.io/
   - Select your app -> App settings -> Secrets
   - Add: `API_URL = "https://contract-analyzer-api.render.com"`

## Option 3: Deploy on Railway.app

1. **Create Railway account**: https://railway.app

2. **Connect GitHub repository**

3. **Create New Service**:
   - Select `contract-analyzer` as the working directory
   - Set `RAILWAY_SERVICE_NAME=backend`

4. **Set Environment Variables**:
   - `PYTHON_VERSION=3.11`

5. **Deploy**: Railway will auto-deploy on push to main

6. **Get Public URL**: From Railway dashboard

7. **Update Streamlit Secrets** with the Railway backend URL

## Option 4: Deploy Backend to Vercel (Node.js required)

This option is more complex. Use Render or Railway instead.

## Fixing the Streamlit Cloud Frontend

1. **Update App Settings**:
   - Go to https://share.streamlit.io/
   - Select your app -> App settings -> Secrets
   - Add the backend API URL:

```toml
API_URL = "https://your-deployed-backend-url.com"
```

2. **Redeploy**: Streamlit automatically redeploys when you make changes

## Testing Locally

```bash
cd contract-analyzer

# Install dependencies
pip install -r requirements.txt

# Run frontend
streamlit run frontend/streamlit_app.py

# In another terminal, run backend
uvicorn app.main:app --reload
```

Visit `http://localhost:8501`

## Troubleshooting

### Still getting 502 error?

1. **Check API_URL**: Verify the API_URL in Streamlit Secrets matches your deployed backend
2. **Check backend status**: Visit your deployed backend URL directly in browser
3. **Check logs**: Look at Streamlit Cloud logs for error details
4. **Test backend directly**: 
   ```bash
   curl -X POST https://your-api-url/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Password123"}'
   ```

### Backend deploy failed?

- Check deployment platform logs
- Ensure all required Python packages are in `requirements.txt`
- Verify environment variables are set correctly

## Key URLs

- **Frontend (Streamlit Cloud)**: https://share.streamlit.io/HadiaAkbar/Contract-Risk-analyzer/main/contract-analyzer/frontend/streamlit_app.py
- **Backend (Deploy to Render/Railway)**: Your backend service URL
- **GitHub**: https://github.com/HadiaAkbar/Contract-Risk-analyzer

## Next Steps

1. Deploy the backend using one of the options above
2. Update Streamlit Secrets with the backend URL
3. Refresh the Streamlit app
4. Login should now work!
