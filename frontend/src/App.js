import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [exchange, setExchange] = useState('NASDAQ');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [popularStocks, setPopularStocks] = useState([]);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch popular stocks on component mount
  useEffect(() => {
    const fetchPopularStocks = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/popular-stocks`);
        if (response.ok) {
          const data = await response.json();
          setPopularStocks(data.popular_stocks);
        }
      } catch (err) {
        console.error('Error fetching popular stocks:', err);
      }
    };

    fetchPopularStocks();
  }, [backendUrl]);

  // Handle stock analysis
  const handleAnalyze = async () => {
    if (!symbol.trim() || !exchange.trim()) {
      setError('Please enter both symbol and exchange');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const response = await fetch(`${backendUrl}/api/analyze-stock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol.trim(),
          exchange: exchange.trim(),
        }),
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

  // Handle quick stock selection
  const handleQuickSelect = (stockSymbol, stockExchange) => {
    setSymbol(stockSymbol);
    setExchange(stockExchange);
  };

  // Format analysis text with proper markdown-style rendering
  const formatAnalysis = (text) => {
    return text
      .replace(/# (.*)/g, '<h1 class="analysis-h1">$1</h1>')
      .replace(/## (.*)/g, '<h2 class="analysis-h2">$1</h2>')
      .replace(/### (.*)/g, '<h3 class="analysis-h3">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/- (.*)/g, '<li>$1</li>')
      .replace(/\n/g, '<br/>');
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
              Get comprehensive stock analysis with AI-powered insights and real-time charts
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Stock Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
            
            <div className="flex items-end">
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔍</span>
                    Analyze Stock
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Popular Stocks */}
          {popularStocks.length > 0 && (
            <div>
              <h3 className="text-lg font-medium text-gray-700 mb-3">Quick Select:</h3>
              <div className="flex flex-wrap gap-2">
                {popularStocks.map((stock, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickSelect(stock.symbol, stock.exchange)}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-sm transition duration-200"
                  >
                    {stock.symbol} ({stock.exchange})
                  </button>
                ))}
              </div>
            </div>
          )}
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
            {/* Chart Section */}
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

            {/* Analysis Report */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                🤖 AI Analysis Report
              </h2>
              <div 
                className="prose prose-lg max-w-none"
                dangerouslySetInnerHTML={{ 
                  __html: formatAnalysis(analysis.analysis) 
                }}
              />
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">Analyzing Stock...</h3>
            <p className="text-gray-500">
              Fetching chart data and generating AI-powered analysis
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm">
            📈 AI Stock Analysis Tool - Powered by Chart-Img API & Gemini AI
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