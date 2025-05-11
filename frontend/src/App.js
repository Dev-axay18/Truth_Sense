import React, { useState } from 'react';
import { Tab } from '@react-tabs/react-tabs';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const [activeTab, setActiveTab] = useState('headline');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const analyzeNews = async () => {
    if (!input.trim()) {
      toast.error('Please enter some content to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/analyze', {
        content: input,
        input_type: activeTab
      });

      setResult(response.data);
      setHistory(prev => [response.data, ...prev].slice(0, 10));
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error('Error analyzing news: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white">
      <nav className="bg-black/30 backdrop-blur-lg border-b border-purple-500/30 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            TruthSense
          </h1>
          <div className="flex space-x-4">
            <button className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition-all">
              History
            </button>
            <button className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition-all">
              Settings
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
            <div className="flex space-x-4 mb-6">
              {['headline', 'article', 'url'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    activeTab === tab
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="mb-6">
              {activeTab === 'article' ? (
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="w-full h-48 bg-gray-800 text-white rounded-lg p-4 border border-purple-500/30 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50"
                  placeholder="Enter your article text here..."
                />
              ) : (
                <input
                  type={activeTab === 'url' ? 'url' : 'text'}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="w-full bg-gray-800 text-white rounded-lg p-4 border border-purple-500/30 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50"
                  placeholder={`Enter your ${activeTab} here...`}
                />
              )}
            </div>

            <button
              onClick={analyzeNews}
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-bold text-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze News'}
            </button>
          </div>

          {result && (
            <div className="mt-8 bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-2xl font-bold mb-4">Analysis Result</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Classification</h3>
                  <p className="text-2xl font-bold text-purple-400">
                    {result.classification}
                  </p>
                </div>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Confidence</h3>
                  <p className="text-2xl font-bold text-blue-400">
                    {result.confidence_score}%
                  </p>
                </div>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Country of Origin</h3>
                  <p className="text-xl text-green-400">{result.country_of_origin}</p>
                </div>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Verification Status</h3>
                  <p className="text-xl text-yellow-400">
                    {result.is_verified ? 'Verified' : 'Unverified'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </div>
  );
}

export default App; 