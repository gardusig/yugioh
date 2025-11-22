import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Cards from './pages/Cards'
import Decks from './pages/Decks'
import DeckDetail from './pages/DeckDetail'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-yugioh-gradient relative overflow-hidden">
        {/* Animated background effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-yugioh-accent/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-yugioh-purple/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        <nav className="relative bg-yugioh-dark/90 backdrop-blur-md border-b-2 border-yugioh-accent/30 shadow-yugioh-glow">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-2xl font-bold yugioh-text-glow text-yugioh-accent hover:text-yugioh-gold transition-colors">
                ⚡ Yu-Gi-Oh! The Sacred Cards ⚡
              </Link>
              <div className="flex gap-6">
                <Link 
                  to="/cards" 
                  className="text-white hover:text-yugioh-accent transition-colors font-medium hover:yugioh-text-glow"
                >
                  Cards
                </Link>
                <Link 
                  to="/decks" 
                  className="text-white hover:text-yugioh-accent transition-colors font-medium hover:yugioh-text-glow"
                >
                  Decks
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="relative container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={
              <div className="text-center py-20">
                <h1 className="text-6xl font-bold mb-4 yugioh-text-glow text-yugioh-accent">
                  Welcome to Yu-Gi-Oh! The Sacred Cards
                </h1>
                <p className="text-xl text-gray-200 mb-8">
                  Browse all 900 cards and explore character decks
                </p>
                <div className="flex gap-4 justify-center">
                  <Link 
                    to="/cards"
                    className="px-8 py-4 bg-yugioh-accent hover:bg-yugioh-gold text-yugioh-dark rounded-lg font-bold transition-all shadow-yugioh-glow hover:scale-105"
                  >
                    View Cards
                  </Link>
                  <Link 
                    to="/decks"
                    className="px-8 py-4 bg-yugioh-blue hover:bg-yugioh-blue/80 text-white rounded-lg font-bold transition-all shadow-lg hover:scale-105"
                  >
                    View Decks
                  </Link>
                </div>
              </div>
            } />
            <Route path="/cards" element={<Cards />} />
            <Route path="/decks" element={<Decks />} />
            <Route path="/decks/:id" element={<DeckDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

