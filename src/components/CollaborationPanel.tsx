'use client'

import { useState, useEffect } from 'react'
import { Users, UserPlus, Crown, Edit, Eye } from 'lucide-react'
import { CompositionResult } from '@/types/music'

interface CollaborationPanelProps {
  composition: CompositionResult | null
  userId: string
}

interface Collaborator {
  id: string
  name: string
  role: 'owner' | 'editor' | 'viewer'
  isOnline: boolean
  avatar?: string
}

export default function CollaborationPanel({ composition, userId }: CollaborationPanelProps) {
  const [collaborators, setCollaborators] = useState<Collaborator[]>([])
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'editor' | 'viewer'>('viewer')
  const [isInviting, setIsInviting] = useState(false)

  useEffect(() => {
    if (composition) {
      // Mock collaborators data
      setCollaborators([
        {
          id: userId,
          name: 'You',
          role: 'owner',
          isOnline: true
        },
        {
          id: '2',
          name: 'Sarah Chen',
          role: 'editor',
          isOnline: true
        },
        {
          id: '3',
          name: 'Mike Rodriguez',
          role: 'viewer',
          isOnline: false
        }
      ])
    }
  }, [composition, userId])

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inviteEmail.trim() || !composition) return

    setIsInviting(true)
    try {
      // API call to invite collaborator
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock delay
      
      // Add to local state
      const newCollaborator: Collaborator = {
        id: Date.now().toString(),
        name: inviteEmail.split('@')[0],
        role: inviteRole,
        isOnline: false
      }
      
      setCollaborators(prev => [...prev, newCollaborator])
      setInviteEmail('')
    } catch (error) {
      console.error('Failed to invite collaborator:', error)
    } finally {
      setIsInviting(false)
    }
  }

  const updateRole = (collaboratorId: string, newRole: 'editor' | 'viewer') => {
    setCollaborators(prev =>
      prev.map(collab =>
        collab.id === collaboratorId ? { ...collab, role: newRole } : collab
      )
    )
  }

  const removeCollaborator = (collaboratorId: string) => {
    setCollaborators(prev => prev.filter(collab => collab.id !== collaboratorId))
  }

  if (!composition) {
    return (
      <div className="p-6 text-center">
        <Users className="h-12 w-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-400 mb-2">No Composition Selected</h3>
        <p className="text-gray-500 text-sm">
          Select a composition to start collaborating
        </p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Invite Section */}
      <div>
        <h3 className="text-lg font-medium mb-4">Invite Collaborators</h3>
        <form onSubmit={handleInvite} className="space-y-4">
          <div>
            <input
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              placeholder="Enter email address"
              className="form-input"
              required
            />
          </div>
          
          <div>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as 'editor' | 'viewer')}
              className="form-select"
            >
              <option value="viewer">Viewer - Can listen and comment</option>
              <option value="editor">Editor - Can edit and modify</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={isInviting || !inviteEmail.trim()}
            className="w-full btn-primary disabled:opacity-50"
          >
            {isInviting ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Sending...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <UserPlus className="mr-2 h-4 w-4" />
                Send Invitation
              </div>
            )}
          </button>
        </form>
      </div>

      {/* Current Collaborators */}
      <div>
        <h3 className="text-lg font-medium mb-4">
          Collaborators ({collaborators.length})
        </h3>
        
        <div className="space-y-3">
          {collaborators.map((collaborator) => (
            <div
              key={collaborator.id}
              className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700"
            >
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {collaborator.name.charAt(0).toUpperCase()}
                  </div>
                  {collaborator.isOnline && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-800"></div>
                  )}
                </div>
                
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{collaborator.name}</span>
                    {collaborator.role === 'owner' && (
                      <Crown className="h-4 w-4 text-yellow-500" />
                    )}
                  </div>
                  <div className="flex items-center space-x-1 text-xs text-gray-400">
                    {collaborator.role === 'editor' ? (
                      <Edit className="h-3 w-3" />
                    ) : collaborator.role === 'viewer' ? (
                      <Eye className="h-3 w-3" />
                    ) : (
                      <Crown className="h-3 w-3" />
                    )}
                    <span className="capitalize">{collaborator.role}</span>
                    <span>•</span>
                    <span className={collaborator.isOnline ? 'text-green-400' : 'text-gray-500'}>
                      {collaborator.isOnline ? 'Online' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>

              {collaborator.role !== 'owner' && collaborator.id !== userId && (
                <div className="flex items-center space-x-2">
                  <select
                    value={collaborator.role}
                    onChange={(e) => updateRole(collaborator.id, e.target.value as 'editor' | 'viewer')}
                    className="text-xs bg-gray-700 border border-gray-600 rounded px-2 py-1"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="editor">Editor</option>
                  </select>
                  
                  <button
                    onClick={() => removeCollaborator(collaborator.id)}
                    className="text-red-400 hover:text-red-300 text-xs"
                  >
                    Remove
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Live Session Status */}
      <div className="border-t border-gray-700 pt-6">
        <h3 className="text-lg font-medium mb-4">Live Session</h3>
        
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 font-medium text-sm">Session Active</span>
          </div>
          <p className="text-gray-300 text-sm">
            Real-time collaboration is enabled. Changes will be synced instantly.
          </p>
        </div>

        <div className="mt-4 space-y-2">
          <h4 className="text-sm font-medium text-gray-400">Recent Activity</h4>
          <div className="space-y-2 text-xs text-gray-500">
            <div>Sarah Chen adjusted tempo to 125 BPM • 2 min ago</div>
            <div>You added piano track • 5 min ago</div>
            <div>Mike Rodriguez left a comment • 8 min ago</div>
          </div>
        </div>
      </div>

      {/* Share Link */}
      <div className="border-t border-gray-700 pt-6">
        <h3 className="text-lg font-medium mb-4">Share Link</h3>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={`https://portal-ai-music.com/collab/${composition.id}`}
            readOnly
            className="form-input flex-1 text-sm"
          />
          <button
            onClick={() => navigator.clipboard?.writeText(`https://portal-ai-music.com/collab/${composition.id}`)}
            className="btn-secondary px-3 py-2 text-sm"
          >
            Copy
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-2">
          Anyone with this link can view the composition. Manage permissions above.
        </p>
      </div>
    </div>
  )
}
