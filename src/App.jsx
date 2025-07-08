import React from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import MusicGenerator from './components/MusicGenerator'
import Pricing from './components/Pricing'
import Footer from './components/Footer'

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <Features />
      <MusicGenerator />
      <Pricing />
      <Footer />
    </div>
  )
}

export default App