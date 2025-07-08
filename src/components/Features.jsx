import React from 'react'
import { 
  Wand2, 
  Download, 
  Shield, 
  Clock, 
  Palette, 
  Headphones,
  Zap,
  Globe
} from 'lucide-react'

const Features = () => {
  const features = [
    {
      icon: Wand2,
      title: 'AI-Powered Generation',
      description: 'Advanced AI models create unique, high-quality music based on your text descriptions.',
      color: 'from-primary-500 to-primary-600'
    },
    {
      icon: Clock,
      title: 'Instant Creation',
      description: 'Generate professional music tracks in seconds, not hours. Perfect for tight deadlines.',
      color: 'from-accent-500 to-accent-600'
    },
    {
      icon: Shield,
      title: 'Royalty-Free',
      description: 'All generated music is 100% royalty-free. Use it anywhere without copyright concerns.',
      color: 'from-green-500 to-green-600'
    },
    {
      icon: Palette,
      title: 'Multiple Genres',
      description: 'From pop and rock to classical and electronic - create music in any style you need.',
      color: 'from-orange-500 to-orange-600'
    },
    {
      icon: Download,
      title: 'High-Quality Export',
      description: 'Download your tracks in multiple formats including WAV, MP3, and FLAC.',
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: Headphones,
      title: 'Professional Sound',
      description: 'Studio-quality audio output that sounds like it was created by professional musicians.',
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: Zap,
      title: 'Fast Processing',
      description: 'Powered by cutting-edge cloud infrastructure for lightning-fast music generation.',
      color: 'from-yellow-500 to-yellow-600'
    },
    {
      icon: Globe,
      title: 'Global Access',
      description: 'Access your music generator from anywhere in the world, 24/7 availability.',
      color: 'from-teal-500 to-teal-600'
    }
  ]

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Powerful <span className="gradient-text">Features</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to create professional music with AI. 
            No musical training required - just describe what you want.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div 
                key={index}
                className="card p-6 group hover:scale-105 transition-all duration-300"
              >
                <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <button className="btn-primary text-lg px-8 py-4">
            Try All Features Free
          </button>
        </div>
      </div>
    </section>
  )
}

export default Features