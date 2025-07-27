import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [exchange, setExchange] = useState('NASDAQ');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('recommendations'); // New state for active tab - starting with recommendations
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Determine backend URL based on environment
  const getBackendUrl = () => {
    return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  };

  const backendUrl = getBackendUrl();

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setError(null);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);
    } else {
      setError('Please select a valid image file');
      setSelectedFile(null);
      setPreviewUrl(null);
    }
  };

  // Handle stock analysis with uploaded image
  const handleAnalyze = async () => {
    if (!symbol.trim() || !exchange.trim()) {
      setError('Please enter both symbol and exchange');
      return;
    }

    if (!selectedFile) {
      setError('Please select a chart image to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('symbol', symbol.trim());
      formData.append('exchange', exchange.trim());
      formData.append('image', selectedFile);

      const response = await fetch(`${backendUrl}/api/analyze-stock`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze stock. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Format analysis text with proper markdown-style rendering
  const formatAnalysis = (text) => {
    return text
      .replace(/# (.*)/g, '<h1 class="analysis-h1">$1</h1>')
      .replace(/## (.*)/g, '<h2 class="analysis-h2">$1</h2>')
      .replace(/### (.*)/g, '<h3 class="analysis-h3">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/• (.*)/g, '<li>$1</li>')
      .replace(/- (.*)/g, '<li>$1</li>')
      .replace(/\n/g, '<br/>');
  };

  // Tab configuration - Reordered to show Recommendations first
  const tabs = [
    { id: 'recommendations', label: 'Recommendations', icon: '📌' },
    { id: 'fundamental', label: 'Fundamental', icon: '📊' },
    { id: 'sentiment', label: 'Sentimental', icon: '💬' },
    { id: 'technical', label: 'Technical', icon: '📈' }
  ];

  // Get current tab content
  const getCurrentTabContent = () => {
    if (!analysis) return null;
    
    switch (activeTab) {
      case 'recommendations':
        return analysis.recommendations || 'Recommendations not available';
      case 'fundamental':
        return analysis.fundamental_analysis || 'Fundamental analysis not available';
      case 'sentiment':
        return analysis.sentiment_analysis || 'Sentiment analysis not available';
      case 'technical':
        return analysis.technical_analysis || 'Technical analysis not available';
      default:
        return 'Please select a tab to view analysis';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              📈 AI Stock Analysis Tool
            </h1>
            <p className="text-lg text-gray-600">
              Upload your stock chart image and get AI-powered analysis with structured insights
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Stock Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stock Symbol
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="e.g., AAPL, TCS"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Exchange
              </label>
              <select
                value={exchange}
                onChange={(e) => setExchange(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="NASDAQ">NASDAQ</option>
                <option value="NYSE">NYSE</option>
                <option value="NSE">NSE (India)</option>
                <option value="BSE">BSE (India)</option>
                <option value="BINANCE">BINANCE</option>
              </select>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Chart Image
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-400 transition-colors">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                  >
                    <span>Upload chart image</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      accept="image/*"
                      className="sr-only"
                      onChange={handleFileSelect}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
              </div>
            </div>
          </div>

          {/* Image Preview */}
          {previewUrl && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-700 mb-3">Image Preview:</h3>
              <div className="flex justify-center">
                <img
                  src={previewUrl}
                  alt="Chart preview"
                  className="max-w-full max-h-64 object-contain rounded-lg shadow-md"
                />
              </div>
            </div>
          )}

          {/* Analyze Button */}
          <div className="flex justify-center">
            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedFile}
              className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <span className="mr-2">🔍</span>
                  Analyze Stock Chart
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-500 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Chart Section - COMMENTED OUT AS REQUESTED
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                📊 {analysis.symbol} Chart ({analysis.exchange})
              </h2>
              <div className="flex justify-center">
                <img
                  src={analysis.chart_image}
                  alt={`${analysis.symbol} Stock Chart`}
                  className="max-w-full h-auto rounded-lg shadow-md"
                />
              </div>
              <p className="text-sm text-gray-500 mt-3 text-center">
                Last updated: {new Date(analysis.timestamp).toLocaleString()}
              </p>
            </div>
            */}

            {/* Multi-Section Analysis Report */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                🤖 AI Analysis Report - Swing Trade
              </h2>
              
              {/* Tab Navigation */}
              <div className="flex flex-wrap border-b border-gray-200 mb-6">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center px-4 py-3 mr-2 mb-2 text-sm font-medium rounded-t-lg transition-colors duration-200 ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-500'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="min-h-[400px]">
                <div 
                  className="prose prose-lg max-w-none"
                  dangerouslySetInnerHTML={{ 
                    __html: formatAnalysis(getCurrentTabContent()) 
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">Analyzing Stock Chart...</h3>
            <p className="text-gray-500">
              Processing your uploaded image and generating AI-powered analysis
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm">
            📈 AI Stock Analysis Tool - Upload & Analyze with Gemini AI
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Disclaimer: This tool is for educational purposes only. Not financial advice.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
