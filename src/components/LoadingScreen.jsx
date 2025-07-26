import React from 'react'
import { Music, Loader2 } from 'lucide-react'

const LoadingScreen = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
      <div className="text-center">
        <div className="flex justify-center mb-8">
          <div className="relative">
            <Music className="w-16 h-16 text-white" />
            <Loader2 className="w-8 h-8 text-purple-300 absolute -top-2 -right-2 animate-spin" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-white mb-4">Portal AI Music</h1>
        <p className="text-xl text-purple-200 mb-8">Loading your musical experience...</p>
        <div className="flex justify-center">
          <div className="w-64 bg-gray-700 rounded-full h-2">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full animate-pulse" style={{ width: '70%' }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingScreen
