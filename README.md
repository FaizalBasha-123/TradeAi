# 📈 AI Stock Analysis Tool

An AI-powered stock analysis application that allows users to upload stock chart images and receive comprehensive analysis using Google's Gemini Pro Vision API.

## 🌟 Features

- **📊 Image Upload**: Drag-and-drop or click to upload stock chart images
- **🤖 AI Analysis**: Get detailed stock analysis using Gemini Pro Vision API
- **📈 Multi-Exchange Support**: NASDAQ, NYSE, NSE, BSE, BINANCE
- **💻 Responsive Design**: Works perfectly on desktop and mobile
- **🔄 Error Handling**: User-friendly error messages and fallback systems
- **⚡ Fast Performance**: Optimized for both localhost and cloud deployment

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd stock-analysis-app

# Run setup script
chmod +x setup.sh
./setup.sh

# Start development servers
npm run dev
```

### Option 2: Manual Setup
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
yarn install

# Go back to root
cd ..
```

## 🔧 Configuration

### 1. Backend Environment Variables

Create `backend/.env` file:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="stock_analysis"
GEMINI_API_KEY=your_gemini_api_key_here
CHART_IMG_API_KEY=your_chartimg_api_key_here  # Optional for legacy support
```

### 2. Frontend Environment Variables

Create `frontend/.env` file:
```env
# For localhost development
REACT_APP_BACKEND_URL=http://localhost:8001

# For production (if using custom backend)
# REACT_APP_BACKEND_URL=https://your-backend-url.com
```

## 🖥️ Development

### Start Both Services
```bash
npm run dev
```

### Start Services Individually
```bash
# Backend only (runs on http://localhost:8001)
npm run backend

# Frontend only (runs on http://localhost:3000)  
npm run frontend
```

### Build for Production
```bash
npm run build
```

## 🌐 Deployment

### 🔹 Vercel Deployment (Recommended)

#### Prerequisites
- GitHub account
- Vercel account (free tier available)
- Gemini API key from Google AI Studio

#### Step-by-Step Deployment

1. **Prepare Repository**
   ```bash
   # Initialize git if not already done
   git init
   git add .
   git commit -m "Initial commit"
   
   # Push to GitHub
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Set Environment Variables in Vercel**
   - Go to your project dashboard
   - Navigate to "Settings" → "Environment Variables"
   - Add the following variables:
   
   | Name | Value | Environment |
   |------|-------|-------------|
   | `GEMINI_API_KEY` | `your_gemini_api_key` | Production, Preview, Development |

4. **Deploy**
   - Click "Deploy"
   - Your app will be available at `https://your-app-name.vercel.app`

#### Vercel Configuration Details

The app includes a `vercel.json` file that handles:
- ✅ Serverless API functions for backend logic
- ✅ Static frontend deployment
- ✅ Automatic routing between frontend and API
- ✅ CORS configuration
- ✅ Environment variable management

### 🔹 Alternative Deployments

#### Railway (Full-Stack)
1. Connect your GitHub repository
2. Deploy both frontend and backend
3. Set environment variables
4. Railway provides both frontend and backend URLs

#### Netlify + Railway
1. **Frontend on Netlify**: Deploy frontend with build command `cd frontend && yarn build`
2. **Backend on Railway**: Deploy backend separately
3. Update `REACT_APP_BACKEND_URL` to point to Railway backend

#### Heroku (Full-Stack)
1. Create two apps: one for frontend, one for backend
2. Deploy using Git push
3. Set environment variables in Heroku dashboard

## 🛠️ API Endpoints

### Health Check
```
GET /api/health
```

### Popular Stocks
```
GET /api/popular-stocks
```

### Upload Image
```
POST /api/upload-image
Content-Type: multipart/form-data
Body: file (image file)
```

### Analyze Stock
```
POST /api/analyze-stock
Content-Type: multipart/form-data
Body: 
  - symbol (string)
  - exchange (string) 
  - image (file)
```

## 🔑 Getting API Keys

### Gemini API Key (Required)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your environment variables

### Chart-Img API Key (Optional)
1. Go to [Chart-Img.com](https://www.chart-img.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to your environment variables (only needed for legacy endpoint)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend
yarn test
```

### Full Test Suite
```bash
npm run test
```

## 📱 Usage

1. **Open the Application**
   - Localhost: `http://localhost:3000`
   - Production: Your Vercel/deployment URL

2. **Upload Chart Image**
   - Click the upload area or drag and drop an image
   - Supported formats: PNG, JPG, GIF (max 10MB)

3. **Enter Stock Details**
   - Stock Symbol (e.g., AAPL, TSLA)
   - Exchange (NASDAQ, NYSE, NSE, BSE, BINANCE)

4. **Get Analysis**
   - Click "Analyze Stock Chart"
   - Wait for AI-powered analysis
   - Review detailed report with technical indicators

## 🔧 Troubleshooting

### Common Issues

#### "HTTP error! status: 502"
- **Cause**: Backend service not running or misconfigured
- **Solution**: Check if backend is running on correct port, verify environment variables

#### "🔄 The AI service is currently busy"
- **Cause**: Gemini API rate limits or temporary unavailability
- **Solution**: Wait a few moments and try again, check API key validity

#### "📁 The uploaded image is too large"
- **Cause**: Image file exceeds 10MB limit
- **Solution**: Compress image or use a smaller file

#### Frontend not connecting to backend
- **Cause**: Incorrect `REACT_APP_BACKEND_URL`
- **Solution**: Verify environment variable matches backend URL

### Logs and Debugging

#### View Backend Logs (Localhost)
```bash
# If using supervisor
sudo tail -f /var/log/supervisor/backend.out.log

# If running directly
python backend/server.py
```

#### View Frontend Logs
```bash
cd frontend
yarn start
# Check browser console for errors
```

#### Vercel Logs
- Go to Vercel dashboard
- Click on your project
- Navigate to "Functions" tab
- Click on any function to view logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Live Demo**: [Your Vercel URL]
- **GitHub**: [Your GitHub Repo]
- **Documentation**: [Your Docs URL]

## 🏗️ Architecture

```
Frontend (React + Tailwind)
    ↓ HTTP Requests
Backend (FastAPI / Vercel Functions)
    ↓ API Calls
Gemini Pro Vision API
    ↓ Analysis
User Interface
```

### Tech Stack
- **Frontend**: React 19, Tailwind CSS, Axios
- **Backend**: FastAPI (localhost) / Python Functions (Vercel)
- **AI**: Google Gemini Pro Vision API
- **Database**: MongoDB (optional)
- **Deployment**: Vercel, Railway, Netlify, Heroku

## 🆘 Support

For issues and questions:
1. Check this README
2. Look at GitHub Issues
3. Create a new issue with detailed information

---

**Made with ❤️ for stock analysis enthusiasts**