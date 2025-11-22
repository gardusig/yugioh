import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchDecks as fetchDecksApi } from '../api/deckApi'

function Decks() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [decks, setDecks] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState(null)

  // Read pagination params from URL
  const pageParam = searchParams.get('page')
  const firstDeckParam = searchParams.get('firstDeck')
  const page = pageParam ? parseInt(pageParam, 10) : null
  const firstDeck = firstDeckParam ? parseInt(firstDeckParam, 10) : null

  useEffect(() => {
    loadDecks()
  }, [page, firstDeck])

  const loadDecks = async () => {
    setLoading(true)
    try {
      const result = await fetchDecksApi({ page, firstDeck, limit: 20 })
      setDecks(result.decks)
      setPagination(result.pagination)
    } catch (error) {
      console.error('Error fetching decks:', error)
    } finally {
      setLoading(false)
    }
  }

  const updatePagination = (newPage, newFirstDeck) => {
    const params = new URLSearchParams()
    if (newFirstDeck) {
      params.set('firstDeck', newFirstDeck)
      params.delete('page')
    } else if (newPage) {
      params.set('page', newPage)
      params.delete('firstDeck')
    }
    setSearchParams(params)
  }

  if (loading && decks.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-2xl">Loading decks...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-5xl font-bold mb-8 text-center yugioh-text-glow text-yugioh-accent">All Decks</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {decks.map((deck) => (
          <Link
            key={deck.id}
            to={`/decks/${deck.id}`}
            className="block bg-yugioh-dark/80 backdrop-blur-sm hover:bg-yugioh-dark rounded-lg p-6 border-2 border-yugioh-accent/40 hover:border-yugioh-accent hover:shadow-card-glow transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-2xl font-bold text-yugioh-accent hover:yugioh-text-glow transition-all">{deck.name}</h2>
              {deck.isPreset && (
                <span className="px-2 py-1 bg-yellow-500 text-gray-900 text-xs font-bold rounded">
                  Preset
                </span>
              )}
            </div>
            
            {deck.description && (
              <p className="text-gray-300 mb-4 line-clamp-2">{deck.description}</p>
            )}

            <div className="space-y-2 text-sm">
              {deck.characterName && (
                <div>
                  <span className="text-gray-400">Character: </span>
                  <span className="text-white">{deck.characterName}</span>
                </div>
              )}
              {deck.archetype && (
                <div>
                  <span className="text-gray-400">Archetype: </span>
                  <span className="text-white">{deck.archetype}</span>
                </div>
              )}
              {deck.mostCommonType && (
                <div>
                  <span className="text-gray-400">Most Common Type: </span>
                  <span className="text-white font-semibold">{deck.mostCommonType}</span>
                </div>
              )}
              <div className="flex justify-between items-center pt-2 border-t border-gray-600">
                <div>
                  <span className="text-gray-400">Cards: </span>
                  <span className="text-white font-bold">{deck.cardCount}/40</span>
                </div>
                <div>
                  <span className="text-gray-400">Cost: </span>
                  <span className={`font-bold ${deck.totalCost > deck.maxCost ? 'text-red-400' : 'text-green-400'}`}>
                    {deck.totalCost}/{deck.maxCost}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {pagination && (
        <div className="flex justify-center items-center gap-4 mt-8">
          <button
            onClick={() => {
              const currentPage = pagination.page || 1
              updatePagination(Math.max(1, currentPage - 1), null)
            }}
            disabled={pagination.page === 1}
            className="px-4 py-2 bg-yugioh-blue rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-yugioh-blue/80 transition-colors"
          >
            Previous
          </button>
          <span className="text-lg">
            Page {pagination.page} of {pagination.totalPages}
          </span>
          <button
            onClick={() => {
              const currentPage = pagination.page || 1
              updatePagination(Math.min(pagination.totalPages, currentPage + 1), null)
            }}
            disabled={pagination.page === pagination.totalPages}
            className="px-4 py-2 bg-yugioh-blue rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-yugioh-blue/80 transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default Decks

