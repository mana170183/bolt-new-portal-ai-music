import React, { useState } from 'react'
import { Music, Menu, X } from 'lucide-react'

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)

  return (
    <header className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-primary-600 to-accent-600 p-2 rounded-lg">
              <Music className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">Portal AI Music</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
              Features
            </a>
            <a href="#generator" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
              Generator
            </a>
            <a href="#pricing" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
              Pricing
            </a>
            <button className="btn-secondary">
              Sign In
            </button>
            <button className="btn-primary">
              Get Started
            </button>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 animate-fade-in">
            <nav className="flex flex-col space-y-4">
              <a href="#features" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
                Features
              </a>
              <a href="#generator" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
                Generator
              </a>
              <a href="#pricing" className="text-gray-700 hover:text-primary-600 transition-colors duration-200">
                Pricing
              </a>
              <div className="flex flex-col space-y-2 pt-4">
                <button className="btn-secondary">
                  Sign In
                </button>
                <button className="btn-primary">
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