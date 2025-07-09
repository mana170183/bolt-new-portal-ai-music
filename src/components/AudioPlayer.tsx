'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react'
import { CompositionResult } from '@/types/music'

interface AudioPlayerProps {
  composition: CompositionResult
  onCompositionUpdate: (composition: CompositionResult) => void
}

export default function AudioPlayer({ composition, onCompositionUpdate }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [composition.audioUrl])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    audio.volume = isMuted ? 0 : volume
  }, [volume, isMuted])

  const togglePlayPause = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
    setIsPlaying(!isPlaying)
  }

  const skipTime = (seconds: number) => {
    const audio = audioRef.current
    if (!audio) return

    audio.currentTime = Math.max(0, Math.min(duration, audio.currentTime + seconds))
  }

  const seekTo = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    const progressBar = progressRef.current
    if (!audio || !progressBar) return

    const rect = progressBar.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const newTime = (clickX / rect.width) * duration

    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="p-4">
      <audio
        ref={audioRef}
        src={composition.audioUrl}
        preload="metadata"
      />
      
      <div className="flex items-center space-x-4">
        {/* Play Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => skipTime(-10)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <SkipBack className="h-5 w-5" />
          </button>
          
          <button
            onClick={togglePlayPause}
            className="p-3 bg-purple-600 hover:bg-purple-700 rounded-full text-white transition-colors"
          >
            {isPlaying ? (
              <Pause className="h-6 w-6" />
            ) : (
              <Play className="h-6 w-6" />
            )}
          </button>
          
          <button
            onClick={() => skipTime(10)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <SkipForward className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="flex-1 flex items-center space-x-3">
          <span className="text-sm text-gray-400 min-w-[40px]">
            {formatTime(currentTime)}
          </span>
          
          <div
            ref={progressRef}
            onClick={seekTo}
            className="flex-1 h-2 bg-gray-700 rounded-full cursor-pointer relative"
          >
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
              style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
            />
            <div
              className="absolute top-1/2 w-3 h-3 bg-white rounded-full transform -translate-y-1/2 shadow-lg"
              style={{ left: `${duration ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
          
          <span className="text-sm text-gray-400 min-w-[40px]">
            {formatTime(duration)}
          </span>
        </div>

        {/* Volume Control */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            {isMuted || volume === 0 ? (
              <VolumeX className="h-5 w-5" />
            ) : (
              <Volume2 className="h-5 w-5" />
            )}
          </button>
          
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={isMuted ? 0 : volume}
            onChange={(e) => {
              const newVolume = Number(e.target.value)
              setVolume(newVolume)
              if (newVolume > 0) setIsMuted(false)
            }}
            className="w-20 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Track Info */}
        <div className="hidden lg:block text-right min-w-[200px]">
          <div className="text-sm font-medium">{composition.title}</div>
          <div className="text-xs text-gray-400">
            {composition.metadata.bpm} BPM • {composition.metadata.key}
          </div>
        </div>
      </div>

      {/* Waveform Visualization */}
      <div className="mt-4">
        <div className="waveform-container">
          <div 
            className="waveform-progress" 
            style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
          />
          {/* Simplified waveform bars */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="audio-visualizer">
              {Array.from({ length: 40 }, (_, i) => (
                <div
                  key={i}
                  className="audio-bar"
                  style={{
                    height: `${Math.random() * 30 + 10}px`,
                    opacity: currentTime > (i / 40) * duration ? 1 : 0.3
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
