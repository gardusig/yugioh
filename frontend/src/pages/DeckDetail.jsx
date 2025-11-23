import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Card3D from '../components/Card3D'
import { fetchDeckById } from '../api/deckApi'

function DeckDetail() {
  const { id } = useParams()
  const [deck, setDeck] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDeck()
  }, [id])

  const loadDeck = async () => {
    setLoading(true)
    try {
      const deckData = await fetchDeckById(parseInt(id, 10))
      setDeck(deckData)
    } catch (error) {
      console.error('Error fetching deck:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-2xl">Loading deck...</div>
      </div>
    )
  }

  if (!deck) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl mb-4">Deck not found</h2>
        <Link to="/decks" className="text-yugioh-accent hover:underline">
          Back to Decks
        </Link>
      </div>
    )
  }

  return (
    <div>
      <Link 
        to="/decks" 
        className="inline-block mb-6 text-yugioh-accent hover:text-white transition-colors"
      >
        ← Back to Decks
      </Link>

      <div className="bg-yugioh-dark/80 backdrop-blur-sm rounded-lg p-6 mb-8 border-2 border-yugioh-accent/50 shadow-card-glow">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-5xl font-bold yugioh-text-glow text-yugioh-accent mb-2">{deck.name}</h1>
            {deck.characterName && (
              <p className="text-xl text-gray-300">Character: {deck.characterName}</p>
            )}
          </div>
          {deck.isPreset && (
            <span className="px-3 py-1 bg-yellow-500 text-gray-900 text-sm font-bold rounded">
              Preset Deck
            </span>
          )}
        </div>

        {deck.description && (
          <p className="text-gray-300 mb-4">{deck.description}</p>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {deck.archetype && (
            <div>
              <span className="text-gray-400">Archetype: </span>
              <span className="text-white font-semibold">{deck.archetype}</span>
            </div>
          )}
          {deck.mostCommonType && (
            <div>
              <span className="text-gray-400">Most Common Type: </span>
              <span className="text-white font-semibold">{deck.mostCommonType}</span>
            </div>
          )}
          <div>
            <span className="text-gray-400">Cards: </span>
            <span className="text-white font-bold">{deck.cards?.length || 0}/40</span>
          </div>
          <div>
            <span className="text-gray-400">Total Cost: </span>
            <span className={`font-bold ${deck.totalCost > deck.maxCost ? 'text-red-400' : 'text-green-400'}`}>
              {deck.totalCost}/{deck.maxCost}
            </span>
          </div>
        </div>
      </div>

      <h2 className="text-4xl font-bold mb-6 yugioh-text-glow text-yugioh-accent">Cards in Deck</h2>
      
      {deck.cards && deck.cards.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 justify-items-center">
          {deck.cards.map((card) => (
            <Card3D key={card.id} card={card} />
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-400 py-10">No cards in this deck</p>
      )}
    </div>
  )
}

export default DeckDetail

