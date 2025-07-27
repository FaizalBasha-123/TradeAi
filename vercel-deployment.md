# 🚀 AI Stock Analysis Tool - Vercel Deployment Guide

This guide provides comprehensive instructions for deploying the AI Stock Analysis Tool to Vercel, including both frontend and backend components.

## 🏗️ Architecture Overview

The application uses a hybrid deployment model:
- **Frontend**: React app deployed to Vercel's global CDN
- **Backend**: Serverless API functions deployed to Vercel
- **Database**: MongoDB Atlas (cloud database)

## 📋 Prerequisites

Before deploying to Vercel, ensure you have:

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **MongoDB Atlas**: Cloud database account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
4. **API Keys**: Gemini AI and Chart-Img API keys ready

## 🔧 Pre-Deployment Setup

### 1. Repository Structure Verification

Ensure your repository has this structure:
```
/
├── api/                 # Vercel serverless functions
│   ├── analyze-stock.py
│   ├── health.py
│   ├── popular-stocks.py
│   └── upload-image.py
├── frontend/           # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── backend/           # Local development backend
│   ├── server.py
│   └── requirements.txt
├── vercel.json        # Vercel configuration
├── requirements.txt   # Root level Python dependencies
└── package.json      # Root level Node.js dependencies
```

### 2. Vercel Configuration File

Ensure your `vercel.json` is properly configured:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/build"
      }
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "PYTHONPATH": "/var/task"
  }
}
```

### 3. Root Package.json Configuration

Create/update `package.json` in the root directory:

```json
{
  "name": "ai-stock-analysis-tool",
  "version": "1.0.0",
  "scripts": {
    "build": "cd frontend && yarn install && yarn build",
    "dev": "cd frontend && yarn dev"
  },
  "dependencies": {},
  "devDependencies": {}
}
```

### 4. Python Requirements for Vercel

Create/update `requirements.txt` in the root directory:

```txt
fastapi>=0.104.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
requests>=2.31.0
emergentintegrations
pydantic>=2.4.0
```

## 🌐 MongoDB Atlas Setup

### 1. Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up/Sign in
3. Create a new cluster (M0 free tier is sufficient for testing)
4. Configure cluster name and region

### 2. Database Access Configuration

1. **Create Database User**:
   - Go to Database Access
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Create username/password
   - Grant "Atlas admin" role

2. **Configure Network Access**:
   - Go to Network Access
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add specific IP ranges for security

### 3. Get Connection String

1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database user password
5. Replace `<dbname>` with your database name (e.g., `stock_analysis`)

Example: `mongodb+srv://username:password@cluster0.xyz.mongodb.net/stock_analysis`

## 🔑 Environment Variables Setup

### Required Environment Variables for Vercel

#### Production Environment Variables (Vercel Dashboard):

```bash
# Database Configuration
MONGO_URL=mongodb+srv://username:password@cluster0.xyz.mongodb.net/stock_analysis

# AI API Keys
GEMINI_API_KEY=your_primary_gemini_api_key
GEMINI_API_KEY_2=your_backup_gemini_api_key_1
GEMINI_API_KEY_3=your_backup_gemini_api_key_2

# Optional External APIs
CHART_IMG_API_KEY=your_chart_img_api_key

# Frontend Configuration
REACT_APP_BACKEND_URL=https://your-app-name.vercel.app
```

### Setting Environment Variables in Vercel:

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable with appropriate values
4. Set environment scope to "Production" and "Preview"

## 📁 Code Modifications for Vercel

### 1. API Endpoints Structure

Ensure your `/api` directory contains serverless functions:

#### `/api/health.py`:
```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "active", "message": "Stock Analysis API is running"}

# Vercel entry point
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### `/api/analyze-stock.py`:
This should contain your main analysis logic adapted for serverless deployment.

### 2. Frontend Configuration Updates

#### Update `frontend/package.json`:
```json
{
  "name": "stock-analysis-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

#### Update API URL Configuration in Frontend:

In `frontend/src/App.js`, ensure the backend URL logic handles Vercel deployment:

```javascript
// Determine backend URL based on environment
const getBackendUrl = () => {
  // For Vercel deployment, use relative API routes
  if (process.env.NODE_ENV === 'production' && window.location.hostname.includes('vercel.app')) {
    return '';  // Use relative URLs for Vercel
  }
  // For localhost or custom backend URL
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
};
```

### 3. Python Dependencies Management

Ensure all Python packages are compatible with Vercel's serverless environment:

```txt
# requirements.txt (root level)
fastapi>=0.104.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
requests>=2.31.0
emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
pydantic>=2.4.0
pymongo>=4.5.0
```

## 🚀 Deployment Process

### Method 1: GitHub Integration (Recommended)

1. **Connect GitHub Repository**:
   - Go to Vercel dashboard
   - Click "New Project"
   - Import your GitHub repository
   - Configure project settings

2. **Configure Build Settings**:
   - Framework Preset: "Other"
   - Build Command: `yarn build`
   - Output Directory: `frontend/build`
   - Install Command: `yarn install`

3. **Set Environment Variables**:
   - Add all required environment variables in Vercel dashboard
   - Ensure MongoDB URL and API keys are set

4. **Deploy**:
   - Click "Deploy"
   - Wait for build and deployment to complete
   - Vercel will provide deployment URL

### Method 2: Vercel CLI Deployment

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy from Project Root**:
```bash
# Navigate to project root
cd /path/to/your/project

# Deploy to Vercel
vercel --prod

# Follow prompts to configure deployment
```

### Method 3: Manual Upload

1. **Build Frontend Locally**:
```bash
cd frontend
yarn install
yarn build
```

2. **Upload to Vercel**:
   - Use Vercel dashboard to manually upload build files
   - Configure API endpoints separately

## 🔧 Post-Deployment Configuration

### 1. Custom Domain (Optional)

1. Go to Vercel project settings
2. Navigate to Domains
3. Add your custom domain
4. Configure DNS settings as instructed

### 2. Environment Variables Verification

Test your deployment by checking:
- `/api/health` endpoint
- Database connectivity
- API key functionality

### 3. Performance Optimization

Configure the following in Vercel dashboard:
- **Functions Region**: Choose region closest to your users
- **Edge Functions**: Enable for better performance if available
- **Analytics**: Enable Vercel Analytics for monitoring

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl https://your-app.vercel.app/api/health
```

### 2. Frontend Access
Visit `https://your-app.vercel.app` in browser

### 3. Full Functionality Test
1. Upload a stock chart image
2. Enter stock symbol and exchange
3. Click "Analyze Stock Chart"
4. Verify all tabs work (Recommendations, Fundamental, Sentimental, Technical)
5. Check that image display is commented out as requested

## 🐛 Troubleshooting Vercel Deployment

### Common Issues and Solutions

#### 1. Build Failures
```bash
# Check build logs in Vercel dashboard
# Common fixes:
- Verify package.json scripts
- Check Node.js version compatibility
- Ensure all dependencies are listed
```

#### 2. API Function Timeout
```bash
# Vercel serverless functions have execution limits
# Solutions:
- Optimize API response time
- Implement proper error handling
- Use async/await appropriately
```

#### 3. Database Connection Issues
```bash
# Check MongoDB Atlas configuration
# Verify:
- Connection string format
- Database user permissions
- Network access settings (IP whitelist)
- Environment variable values
```

#### 4. Environment Variables Not Loading
```bash
# Check Vercel dashboard settings
# Ensure:
- Variables are set for correct environment (Production/Preview)
- No typos in variable names
- Values are properly formatted
```

#### 5. CORS Issues
```python
# Ensure CORS middleware is properly configured in API functions
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Production Monitoring

### 1. Vercel Analytics
- Enable in project settings
- Monitor performance metrics
- Track user engagement

### 2. Error Logging
```python
# Add logging to API functions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use in functions
logger.info("Analysis request received")
logger.error(f"Error occurred: {str(e)}")
```

### 3. Database Monitoring
- Use MongoDB Atlas monitoring dashboard
- Set up alerts for connection issues
- Monitor query performance

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit API keys to repository
- Use Vercel's secure environment variable storage
- Rotate API keys regularly

### 2. CORS Configuration
```python
# Configure CORS appropriately for production
allow_origins=["https://your-domain.com", "https://your-app.vercel.app"]
```

### 3. Input Validation
- Validate all user inputs
- Implement file upload restrictions
- Add rate limiting if needed

### 4. Database Security
- Use MongoDB Atlas built-in security features
- Configure appropriate user permissions
- Enable audit logging

## 📈 Performance Optimization

### 1. Frontend Optimization
- Enable code splitting
- Optimize images and assets
- Use React lazy loading
- Implement proper caching

### 2. API Optimization
- Implement response caching
- Optimize database queries
- Use async operations
- Minimize cold start times

### 3. Vercel-Specific Optimizations
- Configure appropriate regions
- Use Edge Functions where beneficial
- Optimize bundle size

## 🔄 Continuous Deployment

### GitHub Actions Integration
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 📝 Key Files Modified for Vercel

### Files That Need Modification:

1. **`vercel.json`**: Deployment configuration
2. **`requirements.txt`**: Python dependencies
3. **`package.json`**: Node.js configuration
4. **`/api/*`**: Serverless API functions
5. **Frontend environment handling**: Backend URL logic

### Files That Don't Change:
- Core React components structure
- Main application logic
- Database models (if any)
- CSS/styling files

## 🎯 Post-Deployment Checklist

- [ ] Health endpoint responding
- [ ] Database connection working
- [ ] File upload functionality working
- [ ] All analysis tabs working correctly
- [ ] Recommendations tab appears first
- [ ] Chart image display is commented out
- [ ] Error handling working properly
- [ ] Mobile responsiveness verified
- [ ] Performance metrics acceptable
- [ ] Security configurations in place

## 🆘 Emergency Rollback

If deployment fails:

1. **Revert to Previous Deployment**:
   - Go to Vercel dashboard
   - Select previous working deployment
   - Click "Promote to Production"

2. **Fix and Redeploy**:
   - Fix issues in code
   - Test locally first
   - Push to GitHub for automatic redeployment

## 📞 Support Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas Support**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **FastAPI Deployment**: [fastapi.tiangolo.com/deployment](https://fastapi.tiangolo.com/deployment/)
- **React Deployment**: [create-react-app.dev/docs/deployment](https://create-react-app.dev/docs/deployment/)

## 🎉 Success Indicators

Your deployment is successful when:
- Application loads at Vercel URL
- All API endpoints respond correctly
- Database operations work
- File uploads process successfully
- AI analysis generates results
- All four analysis tabs function properly
- Recommendations tab shows first by default
- Chart image section is properly hidden

Happy deploying! 🚀