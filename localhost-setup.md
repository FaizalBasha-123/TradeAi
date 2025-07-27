# 📈 AI Stock Analysis Tool - Localhost Setup Guide

This guide will help you set up and run the AI Stock Analysis Tool on your local development environment.

## 🔧 Prerequisites

Before setting up the application, ensure you have the following installed on your system:

- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download here](https://python.org/)
- **Yarn** package manager - Install with: `npm install -g yarn`
- **Git** - [Download here](https://git-scm.com/)

## 📁 Project Structure

```
/app/
├── backend/         # FastAPI Python backend
│   ├── server.py    # Main backend server
│   ├── requirements.txt
│   └── .env         # Backend environment variables
├── frontend/        # React frontend
│   ├── src/
│   ├── package.json
│   └── .env         # Frontend environment variables
└── api/            # Vercel API endpoints
```

## 🚀 Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <your-repository-url>
cd app
```

### 2. Backend Setup

#### a. Navigate to Backend Directory
```bash
cd backend
```

#### b. Create Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### c. Install Python Dependencies
```bash
pip install -r requirements.txt

# Also install emergent integrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

#### d. Configure Environment Variables
Create a `.env` file in the backend directory:

```bash
# backend/.env
MONGO_URL=mongodb://localhost:27017/stock_analysis
GEMINI_API_KEY=your_gemini_api_key_here
CHART_IMG_API_KEY=your_chart_img_api_key_here
```

**Required API Keys:**
- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Chart-Img API Key**: Get from [Chart-Img.com](https://chart-img.com/) (optional, used for legacy features)

#### e. Install and Start MongoDB (if not using cloud MongoDB)
```bash
# On macOS with Homebrew:
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu/Debian:
sudo apt-get install mongodb
sudo systemctl start mongodb

# On Windows:
# Download and install MongoDB Community Server from mongodb.com
```

#### f. Start Backend Server
```bash
# Make sure you're in the backend directory
cd backend

# Start the FastAPI server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The backend will be available at: `http://localhost:8001`

### 3. Frontend Setup

#### a. Navigate to Frontend Directory (new terminal)
```bash
cd frontend
```

#### b. Install Node.js Dependencies
```bash
# Install dependencies using Yarn
yarn install
```

#### c. Configure Environment Variables
Create a `.env` file in the frontend directory:

```bash
# frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### d. Start Frontend Development Server
```bash
# Start React development server
yarn start
```

The frontend will be available at: `http://localhost:3000`

## 🌐 Application URLs

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8001`
- **API Documentation**: `http://localhost:8001/docs` (Swagger UI)
- **API Health Check**: `http://localhost:8001/api/health`

## 🔍 Testing the Application

1. **Health Check**: Visit `http://localhost:8001/api/health` to ensure backend is running
2. **Frontend Access**: Open `http://localhost:3000` in your browser
3. **Stock Analysis**: 
   - Enter a stock symbol (e.g., AAPL, TCS)
   - Select exchange (NASDAQ, NSE, etc.)
   - Upload a stock chart image
   - Click "Analyze Stock Chart"
   - View results in the tabbed interface (Recommendations, Fundamental, Sentimental, Technical)

## 🛠️ Development Workflow

### Running Both Services Simultaneously

#### Option 1: Using Supervisor (Recommended)
```bash
# Install supervisor
pip install supervisor

# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status

# View logs
sudo supervisorctl tail -f backend
sudo supervisorctl tail -f frontend
```

#### Option 2: Manual Terminal Management
```bash
# Terminal 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn start
```

### Hot Reload Configuration

- **Frontend**: React development server has hot reload enabled by default
- **Backend**: FastAPI with `--reload` flag enables automatic restart on code changes

### Installing New Dependencies

#### Backend Dependencies
```bash
cd backend
pip install <package-name>
pip freeze > requirements.txt  # Update requirements file
```

#### Frontend Dependencies
```bash
cd frontend
yarn add <package-name>  # For runtime dependencies
yarn add -D <package-name>  # For development dependencies
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Backend Not Starting
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill process if needed
kill -9 <PID>

# Check Python virtual environment
which python
pip list
```

#### 2. Frontend Not Starting
```bash
# Check if port 3000 is in use
lsof -i :3000

# Clear node modules and reinstall
rm -rf node_modules yarn.lock
yarn install

# Check Node.js version
node --version
yarn --version
```

#### 3. MongoDB Connection Issues
```bash
# Check MongoDB status
brew services list | grep mongodb  # macOS
sudo systemctl status mongodb      # Linux

# Check connection
mongo --eval "db.stats()"

# MongoDB logs location
# macOS: /usr/local/var/log/mongodb/
# Linux: /var/log/mongodb/
```

#### 4. API Key Issues
- Verify API keys are correctly set in `.env` files
- Check API key permissions and quotas
- Test API keys independently with curl commands

#### 5. CORS Issues
- Ensure backend CORS middleware is properly configured
- Check that frontend is making requests to correct backend URL
- Verify `REACT_APP_BACKEND_URL` environment variable

### Useful Commands

```bash
# Check backend logs
tail -f backend/logs/server.log

# Check process using ports
lsof -i :3000  # Frontend
lsof -i :8001  # Backend

# Supervisor commands
sudo supervisorctl restart all
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
sudo supervisorctl status

# Environment validation
env | grep REACT_APP
env | grep GEMINI
env | grep MONGO
```

## 📊 Application Features

### Current Functionality
- **Multi-Section Analysis**: 4 types of analysis (Recommendations, Fundamental, Sentimental, Technical)
- **Image Upload**: Drag-and-drop chart image upload
- **AI Integration**: Gemini AI for comprehensive stock analysis
- **Tabbed Interface**: Switch between different analysis sections
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Works on desktop and mobile devices

### Analysis Sections Order
1. **📌 Recommendations** (Default/First tab)
2. **📊 Fundamental**
3. **💬 Sentimental** 
4. **📈 Technical**

## 🔄 Development Best Practices

1. **Always use virtual environment** for Python dependencies
2. **Use Yarn instead of npm** for Node.js packages
3. **Keep .env files secure** and never commit them to version control
4. **Test API endpoints** using the Swagger UI at `/docs`
5. **Check logs regularly** for errors and debugging information
6. **Use supervisor** for managing multiple services in development

## 📝 File Modifications for Localhost

### Files That May Need Modification:

#### Backend (`backend/server.py`):
- Ensure CORS middleware allows localhost origins
- Verify MongoDB connection string in environment
- Check API key configuration

#### Frontend (`frontend/src/App.js`):
- Confirm `REACT_APP_BACKEND_URL` usage for API calls
- Verify image upload functionality
- Check tab ordering (Recommendations first)

#### Environment Files:
- `backend/.env`: MongoDB URL, API keys
- `frontend/.env`: Backend URL configuration

### No Modifications Needed:
- Port configurations (3000 for frontend, 8001 for backend)
- Service binding addresses
- Supervisor configurations (if using)

## 🎯 Next Steps

After successful localhost setup:
1. Test all features thoroughly
2. Add your own API keys for external services
3. Customize analysis prompts if needed
4. Consider setting up staging environment
5. Review deployment options (see vercel-deployment.md)

## 📞 Support

For issues with localhost setup:
1. Check this troubleshooting guide
2. Review application logs
3. Verify all prerequisites are installed
4. Test individual components (backend, frontend, database)
5. Check environment variable configuration

Happy coding! 🚀