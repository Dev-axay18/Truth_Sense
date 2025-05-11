import { useState, useEffect } from 'react'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs'
import axios from 'axios'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import History from './components/History'
import ThemeSwitcher from './components/ThemeSwitcher'
import URLPreview from './components/URLPreview'

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('headline')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const [theme, setTheme] = useState('Dark')
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'Dark'
    setTheme(savedTheme)
    document.documentElement.classList.toggle('dark', savedTheme === 'Dark')
  }, [])

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'Dark')
  }

  const analyzeNews = async () => {
    if (!input.trim()) {
      toast.error('Please enter some content to analyze')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('/api/analyze', {
        content: input,
        advanced_analysis: showAdvanced
      })

      const newResult = {
        ...response.data,
        content: input,
        timestamp: new Date().toISOString()
      }

      setResult(newResult)
      setHistory(prev => [newResult, ...prev].slice(0, 10))
      toast.success('Analysis complete!')
    } catch (error) {
      console.error('Error details:', error.response?.data || error.message)
      toast.error('Error analyzing news: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleSelectHistory = (item) => {
    setInput(item.content)
    setResult(item)
    setIsHistoryOpen(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white">
      <nav className="bg-black/30 backdrop-blur-lg border-b border-purple-500/30 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            TruthSense
          </h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsHistoryOpen(true)}
              className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition-all"
            >
              History
            </button>
            <ThemeSwitcher currentTheme={theme} onThemeChange={handleThemeChange} />
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
            <Tabs
              selectedIndex={['headline', 'article', 'url'].indexOf(activeTab)}
              onSelect={(index) => setActiveTab(['headline', 'article', 'url'][index])}
              className="space-y-4"
            >
              <TabList className="flex space-x-4">
                {['headline', 'article', 'url'].map((tab) => (
                  <Tab
                    key={tab}
                    className={`px-4 py-2 rounded-lg transition-all cursor-pointer ${
                      activeTab === tab
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </Tab>
                ))}
              </TabList>

              <div className="space-y-4">
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

                {activeTab === 'url' && <URLPreview url={input} />}

                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-sm text-gray-400 hover:text-white"
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                  </button>
                </div>

                {showAdvanced && (
                  <div className="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
                    <h3 className="text-lg font-semibold mb-2">Advanced Analysis Options</h3>
                    <div className="space-y-2">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          className="rounded border-gray-600 bg-gray-700 text-purple-500 focus:ring-purple-500"
                        />
                        <span>Include source credibility analysis</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          className="rounded border-gray-600 bg-gray-700 text-purple-500 focus:ring-purple-500"
                        />
                        <span>Perform sentiment analysis</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          className="rounded border-gray-600 bg-gray-700 text-purple-500 focus:ring-purple-500"
                        />
                        <span>Check for similar articles</span>
                      </label>
                    </div>
                  </div>
                )}

                <button
                  onClick={analyzeNews}
                  disabled={loading}
                  className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-bold text-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50"
                >
                  {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    'Analyze News'
                  )}
                </button>
              </div>
            </Tabs>
          </div>

          {result && (
            <div className="mt-8 bg-black/30 backdrop-blur-lg rounded-xl p-6 border border-purple-500/30">
              <h2 className="text-2xl font-bold mb-4">Analysis Result</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Classification</h3>
                  <p className="text-2xl font-bold text-purple-400">{result.classification}</p>
                </div>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Confidence</h3>
                  <p className="text-2xl font-bold text-blue-400">{result.confidence_score}%</p>
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

              {result.source_metadata && (
                <div className="mt-4 bg-gray-800/50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Source Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-400">Source Name</p>
                      <p className="text-white">{result.source_metadata.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Publication Date</p>
                      <p className="text-white">{result.source_metadata.date}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Author</p>
                      <p className="text-white">{result.source_metadata.author}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Domain</p>
                      <p className="text-white">{result.source_metadata.domain}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* History Modal */}
      {isHistoryOpen && (
        <History
          isOpen={isHistoryOpen}
          onClose={() => setIsHistoryOpen(false)}
          history={history}
          onSelect={handleSelectHistory}
        />
      )}

      <ToastContainer position="bottom-right" autoClose={4000} theme="dark" />
    </div>
  )
}

export default App
