#!/bin/bash

echo "🚀 Setting up Stock Analysis App for localhost development..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if yarn is installed
if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn is required but not installed. Installing yarn..."
    npm install -g yarn
fi

echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "📦 Installing frontend dependencies..."
cd frontend
yarn install
cd ..

echo "✅ Setup completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Create backend/.env file with your API keys (see README.md)"
echo "2. Create frontend/.env file with backend URL (see README.md)"
echo "3. Run 'npm run dev' to start both services"
echo ""
echo "📖 For detailed instructions, see README.md"