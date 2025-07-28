import React, { useState } from 'react'
import { Music, Menu, X } from 'lucide-react'

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)

  return (
    <header className="bg-white/98 backdrop-blur-sm border-b border-gray-300 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 p-2 rounded-lg shadow-lg">
              <Music className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Portal AI Music</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
              Features
            </a>
            <a href="#generator" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
              Generator
            </a>
            <a href="#pricing" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
              Pricing
            </a>
            <button className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105">
              Sign In
            </button>
            <button className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105">
              Get Started
            </button>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            {isMenuOpen ? <X className="h-6 w-6 text-gray-800" /> : <Menu className="h-6 w-6 text-gray-800" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-300 animate-fade-in bg-white/98">
            <nav className="flex flex-col space-y-4">
              <a href="#features" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
                Features
              </a>
              <a href="#generator" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
                Generator
              </a>
              <a href="#pricing" className="text-gray-800 hover:text-blue-600 transition-colors duration-200 font-medium">
                Pricing
              </a>
              <div className="flex flex-col space-y-2 pt-4">
                <button className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-md">
                  Sign In
                </button>
                <button className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-md">
                  Get Started
                </button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header