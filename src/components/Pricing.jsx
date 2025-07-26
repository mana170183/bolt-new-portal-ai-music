import React from 'react'
import { Check, Star, Zap } from 'lucide-react'

const Pricing = () => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for trying out AI music generation',
      features: [
        '5 tracks per month',
        'Up to 30 seconds per track',
        'Basic genres',
        'MP3 downloads',
        'Personal use only'
      ],
      buttonText: 'Get Started Free',
      buttonStyle: 'btn-secondary',
      popular: false
    },
    {
      name: 'Creator',
      price: '$19',
      period: 'per month',
      description: 'Ideal for content creators and small businesses',
      features: [
        '100 tracks per month',
        'Up to 3 minutes per track',
        'All genres and moods',
        'WAV + MP3 downloads',
        'Commercial use included',
        'Priority generation',
        'Email support'
      ],
      buttonText: 'Start Creating',
      buttonStyle: 'btn-primary',
      popular: true
    },
    {
      name: 'Professional',
      price: '$49',
      period: 'per month',
      description: 'For agencies and professional creators',
      features: [
        'Unlimited tracks',
        'Up to 10 minutes per track',
        'All genres and moods',
        'All formats (WAV, MP3, FLAC)',
        'Commercial use included',
        'Instant generation',
        'Priority support',
        'Custom AI training',
        'API access'
      ],
      buttonText: 'Go Professional',
      buttonStyle: 'btn-primary',
      popular: false
    }
  ]

  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Simple <span className="gradient-text">Pricing</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Choose the perfect plan for your music creation needs. 
            All plans include royalty-free usage rights.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`card p-8 relative ${
                plan.popular 
                  ? 'ring-2 ring-primary-500 transform scale-105' 
                  : ''
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-primary-600 to-accent-600 text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center space-x-1">
                    <Star className="h-4 w-4" />
                    <span>Most Popular</span>
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold gradient-text">
                    {plan.price}
                  </span>
                  <span className="text-gray-600 ml-2">
                    {plan.period}
                  </span>
                </div>
                <p className="text-gray-600">
                  {plan.description}
                </p>
              </div>

              {/* Features List */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <Check className="h-5 w-5 text-green-500" />
                    </div>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <button className={`w-full ${plan.buttonStyle} ${
                plan.popular ? 'shadow-xl' : ''
              }`}>
                {plan.popular && <Zap className="h-4 w-4 mr-2" />}
                {plan.buttonText}
              </button>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="text-center mt-16">
          <p className="text-gray-600 mb-4">
            All plans include 100% royalty-free music with commercial usage rights
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="btn-secondary">
              Compare All Features
            </button>
            <button className="btn-primary">
              Start Free Trial
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Pricing