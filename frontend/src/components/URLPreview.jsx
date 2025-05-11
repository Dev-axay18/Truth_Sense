import { useState, useEffect } from 'react'
import { LinkIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'

export default function URLPreview({ url }) {
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!url) {
      setPreview(null)
      return
    }

    const fetchPreview = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`http://localhost:8000/api/preview-url?url=${encodeURIComponent(url)}`)
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Failed to fetch preview')
        }
        const data = await response.json()
        setPreview(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    const timeoutId = setTimeout(fetchPreview, 1000)
    return () => clearTimeout(timeoutId)
  }, [url])

  if (!url) return null

  return (
    <div className="mt-4 rounded-lg border border-gray-700 bg-gray-800/50 p-6">
      {loading ? (
        <div className="flex items-center justify-center space-x-3 py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
          <span className="text-gray-400">Loading preview...</span>
        </div>
      ) : error ? (
        <div className="flex items-center space-x-3 text-red-400 py-4">
          <ExclamationCircleIcon className="h-6 w-6 flex-shrink-0" />
          <div className="flex-1">
            <p className="font-medium">Failed to load preview</p>
            <p className="text-sm text-red-300 mt-1">{error}</p>
          </div>
        </div>
      ) : preview ? (
        <div className="space-y-4">
          {preview.image && (
            <div className="relative h-48 w-full overflow-hidden rounded-lg">
              <img
                src={preview.image}
                alt={preview.title}
                className="h-full w-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
            </div>
          )}
          <div className="space-y-3">
            <h3 className="text-xl font-semibold text-white">{preview.title || 'No Title'}</h3>
            {preview.description && (
              <p className="text-base text-gray-300 leading-relaxed">{preview.description}</p>
            )}
            <div className="flex items-center space-x-3 text-sm text-gray-400">
              <LinkIcon className="h-5 w-5" />
              <span className="truncate">{url}</span>
            </div>
            {preview.author && (
              <div className="text-sm text-gray-400">
                By {preview.author}
              </div>
            )}
            {preview.domain && (
              <div className="text-sm text-gray-400">
                From {preview.domain}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}
