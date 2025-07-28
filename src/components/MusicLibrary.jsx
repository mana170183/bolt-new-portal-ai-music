import React, { useState, useEffect, useRef } from 'react'
import { 
  Play, 
  Pause, 
  Download, 
  Search,
  Filter,
  Clock,
  Calendar,
  Music,
  Heart,
  Share2,
  Trash2,
  Tag,
  Grid,
  List,
  SortAsc
} from 'lucide-react'

const MusicLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('date') // 'date', 'name', 'duration'
  const [filterGenre, setFilterGenre] = useState('all')
  const [tracks, setTracks] = useState([])
  const [playingTrack, setPlayingTrack] = useState(null)
  const audioRef = useRef(null)

  // Mock data for demonstration
  useEffect(() => {
    const mockTracks = [
      {
        id: 1,
        title: "Epic Adventure",
        genre: "orchestral",
        duration: 180,
        createdAt: "2024-01-15",
        plays: 245,
        liked: true,
        tags: ["cinematic", "epic", "adventure"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      },
      {
        id: 2,
        title: "Synthwave Nights",
        genre: "electronic",
        duration: 240,
        createdAt: "2024-01-14",
        plays: 189,
        liked: false,
        tags: ["synthwave", "retro", "80s"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      },
      {
        id: 3,
        title: "Jazz Cafe",
        genre: "jazz",
        duration: 210,
        createdAt: "2024-01-13",
        plays: 156,
        liked: true,
        tags: ["smooth", "cafe", "relaxing"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      },
      {
        id: 4,
        title: "Rock Anthem",
        genre: "rock",
        duration: 195,
        createdAt: "2024-01-12",
        plays: 312,
        liked: false,
        tags: ["energetic", "powerful", "guitar"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      },
      {
        id: 5,
        title: "Ambient Dreams",
        genre: "ambient",
        duration: 420,
        createdAt: "2024-01-11",
        plays: 89,
        liked: true,
        tags: ["peaceful", "meditation", "space"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      },
      {
        id: 6,
        title: "Hip Hop Beat",
        genre: "hip-hop",
        duration: 150,
        createdAt: "2024-01-10",
        plays: 278,
        liked: false,
        tags: ["urban", "beat", "rap"],
        waveform: "data:image/svg+xml,...",
        audioUrl: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3"
      }
    ]
    setTracks(mockTracks)
  }, [])

  const filteredTracks = tracks
    .filter(track => {
      const matchesSearch = track.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           track.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      const matchesGenre = filterGenre === 'all' || track.genre === filterGenre
      return matchesSearch && matchesGenre
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.title.localeCompare(b.title)
        case 'duration':
          return b.duration - a.duration
        case 'plays':
          return b.plays - a.plays
        default: // date
          return new Date(b.createdAt) - new Date(a.createdAt)
      }
    })

  const togglePlay = async (trackId) => {
    const track = tracks.find(t => t.id === trackId);
    if (!track?.audioUrl || !audioRef.current) {
      console.warn('No audio URL or audio element available');
      return;
    }

    try {
      if (playingTrack === trackId) {
        // Currently playing this track, pause it
        audioRef.current.pause();
        setPlayingTrack(null);
      } else {
        // Play this track
        audioRef.current.src = track.audioUrl;
        await audioRef.current.play();
        setPlayingTrack(trackId);
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      setPlayingTrack(null);
    }
  }

  const toggleLike = (trackId) => {
    setTracks(prev => prev.map(track => 
      track.id === trackId ? { ...track, liked: !track.liked } : track
    ))
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const genres = ['all', 'orchestral', 'electronic', 'jazz', 'rock', 'ambient', 'hip-hop']

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Music Library</h2>
        <p className="text-gray-600">Manage and explore your generated music collection</p>
      </div>

      {/* Controls */}
      <div className="mb-8 space-y-4">
        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search tracks, tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={filterGenre}
            onChange={(e) => setFilterGenre(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {genres.map(genre => (
              <option key={genre} value={genre}>
                {genre === 'all' ? 'All Genres' : genre.charAt(0).toUpperCase() + genre.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* View Controls */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <SortAsc className="w-4 h-4 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="text-sm border border-gray-300 rounded px-3 py-1 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="date">Sort by Date</option>
                <option value="name">Sort by Name</option>
                <option value="duration">Sort by Duration</option>
                <option value="plays">Sort by Plays</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-purple-100 text-purple-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-purple-100 text-purple-600' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Tracks Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTracks.map(track => (
            <div key={track.id} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{track.title}</h3>
                  <p className="text-sm text-gray-600 capitalize">{track.genre}</p>
                </div>
                <button
                  onClick={() => toggleLike(track.id)}
                  className={`p-1 rounded ${track.liked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
                >
                  <Heart className={`w-4 h-4 ${track.liked ? 'fill-current' : ''}`} />
                </button>
              </div>

              {/* Waveform Visualization */}
              <div className="bg-white rounded-lg p-3 mb-4">
                <div className="flex items-center justify-center h-16 bg-gradient-to-r from-purple-200 to-blue-200 rounded">
                  <div className="flex items-end space-x-1">
                    {Array.from({ length: 20 }, (_, i) => (
                      <div
                        key={i}
                        className="bg-purple-500 rounded-sm"
                        style={{
                          height: `${Math.random() * 40 + 10}px`,
                          width: '3px'
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {formatDuration(track.duration)}
                  </div>
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 mr-1" />
                    {formatDate(track.createdAt)}
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-4">
                {track.tags.map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-white text-xs text-purple-600 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => togglePlay(track.id)}
                  className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {playingTrack === track.id ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  <span>{playingTrack === track.id ? 'Pause' : 'Play'}</span>
                </button>

                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded">
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-blue-600 rounded">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTracks.map(track => (
            <div key={track.id} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <button
                    onClick={() => togglePlay(track.id)}
                    className="flex items-center justify-center w-10 h-10 bg-purple-600 hover:bg-purple-700 text-white rounded-full"
                  >
                    {playingTrack === track.id ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>

                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{track.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="capitalize">{track.genre}</span>
                      <span>{formatDuration(track.duration)}</span>
                      <span>{formatDate(track.createdAt)}</span>
                      <span>{track.plays} plays</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {track.tags.slice(0, 3).map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-purple-100 text-xs text-purple-600 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleLike(track.id)}
                    className={`p-2 rounded ${track.liked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
                  >
                    <Heart className={`w-4 h-4 ${track.liked ? 'fill-current' : ''}`} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 rounded">
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-blue-600 rounded">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredTracks.length === 0 && (
        <div className="text-center py-12">
          <Music className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No tracks found</h3>
          <p className="text-gray-600">Try adjusting your search or filters</p>
        </div>
      )}

      {/* Hidden audio element for playback */}
      <audio 
        ref={audioRef} 
        onEnded={() => setPlayingTrack(null)}
        onError={() => setPlayingTrack(null)}
      />
    </div>
  )
}

export default MusicLibrary
