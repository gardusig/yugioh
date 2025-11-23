import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import Card3D from '../components/Card3D'
import { fetchCards as fetchCardsApi } from '../api/cardApi'

function Cards() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState(null)

  // Read pagination params from URL
  const pageParam = searchParams.get('page')
  const firstCardParam = searchParams.get('firstCard')
  const page = pageParam ? parseInt(pageParam, 10) : null
  const firstCard = firstCardParam ? parseInt(firstCardParam, 10) : null

  useEffect(() => {
    loadCards()
  }, [page, firstCard])

  const loadCards = async () => {
    setLoading(true)
    try {
      const result = await fetchCardsApi({ page, firstCard, limit: 24 })
      setCards(result.cards)
      setPagination(result.pagination)
    } catch (error) {
      console.error('Error fetching cards:', error)
    } finally {
      setLoading(false)
    }
  }

  const updatePagination = (newPage, newFirstCard) => {
    const params = new URLSearchParams()
    if (newFirstCard) {
      params.set('firstCard', newFirstCard)
      params.delete('page')
    } else if (newPage) {
      params.set('page', newPage)
      params.delete('firstCard')
    }
    setSearchParams(params)
  }

  if (loading && cards.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-2xl">Loading cards...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-5xl font-bold mb-8 text-center yugioh-text-glow text-yugioh-accent">All Cards</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 justify-items-center">
        {cards.map((card) => (
          <Card3D key={card.id} card={card} />
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

export default Cards

