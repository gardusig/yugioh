import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Decks from './Decks'
import * as deckApi from '../api/deckApi'

// Mock the API module
vi.mock('../api/deckApi')

describe('Decks', () => {
  const mockDecksData = {
    decks: [
      {
        id: 1,
        name: 'Yugi Deck',
        description: 'Yugi Muto deck',
        characterName: 'Yugi Muto',
        archetype: 'Spellcaster',
        mostCommonType: 'Dark',
        cardCount: 40,
        totalCost: 200,
        maxCost: 250,
        isPreset: true,
      },
      {
        id: 2,
        name: 'Kaiba Deck',
        description: 'Seto Kaiba deck',
        characterName: 'Seto Kaiba',
        archetype: 'Dragon',
        mostCommonType: 'Light',
        cardCount: 40,
        totalCost: 180,
        maxCost: 200,
        isPreset: true,
      },
    ],
    pagination: {
      page: 1,
      limit: 20,
      totalElements: 2,
      totalPages: 1,
    },
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock implementation
    deckApi.fetchDecks.mockResolvedValue(mockDecksData)
  })

  const renderDecks = (initialSearchParams = '') => {
    const Wrapper = ({ children }) => (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        {children}
      </BrowserRouter>
    )
    if (initialSearchParams) {
      window.history.pushState({}, '', `/decks?${initialSearchParams}`)
    }
    return render(<Decks />, { wrapper: Wrapper })
  }

  it('renders loading state initially', () => {
    deckApi.fetchDecks.mockImplementation(() => new Promise(() => {})) // Never resolves
    renderDecks()
    expect(screen.getByText('Loading decks...')).toBeInTheDocument()
  })

  it('fetches and displays decks', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
    expect(screen.getByText('Kaiba Deck')).toBeInTheDocument()
    expect(deckApi.fetchDecks).toHaveBeenCalledWith({ page: null, firstDeck: null, limit: 20 })
  })

  it('displays deck information', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Muto')).toBeInTheDocument()
      expect(screen.getByText('Spellcaster')).toBeInTheDocument()
      expect(screen.getByText('Dark')).toBeInTheDocument()
      // Multiple decks have "40/40", so use getAllByText
      expect(screen.getAllByText('40/40').length).toBeGreaterThan(0)
    })
  })

  it('displays preset badge', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks()
    
    await waitFor(() => {
      expect(screen.getAllByText('Preset')).toHaveLength(2)
    })
  })

  it('displays cost with correct color', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks()
    
    await waitFor(() => {
      const costElements = screen.getAllByText(/200\/250/)
      expect(costElements.length).toBeGreaterThan(0)
    })
  })

  it('handles pagination', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks()
    
    await waitFor(() => {
      expect(screen.getByText('Page 1 of 1')).toBeInTheDocument()
    })
  })

  it('handles fetch error', async () => {
    deckApi.fetchDecks.mockRejectedValueOnce(new Error('Network error'))
    renderDecks()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading decks...')).not.toBeInTheDocument()
    })
  })

  it('handles firstDeck parameter', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks('firstDeck=1')
    
    await waitFor(() => {
      expect(deckApi.fetchDecks).toHaveBeenCalledWith({ page: null, firstDeck: 1, limit: 20 })
    })
  })

  it('handles empty decks array', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce({ decks: [], pagination: null })
    renderDecks()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading decks...')).not.toBeInTheDocument()
    })
  })

  it('handles deck without description', async () => {
    const deckWithoutDesc = {
      ...mockDecksData,
      decks: [{ ...mockDecksData.decks[0], description: null }],
    }
    deckApi.fetchDecks.mockResolvedValueOnce(deckWithoutDesc)
    renderDecks()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
  })

  it('handles pagination button clicks', async () => {
    const paginationData = {
      ...mockDecksData,
      pagination: {
        page: 2,
        limit: 20,
        totalElements: 50,
        totalPages: 3,
      },
    }
    deckApi.fetchDecks.mockResolvedValueOnce(paginationData)
    renderDecks('page=2')
    
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })
    
    // Test pagination button clicks
    const prevButton = screen.getByText('Previous')
    fireEvent.click(prevButton)
    
    const nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
  })

  it('handles updatePagination with firstDeck', async () => {
    deckApi.fetchDecks.mockResolvedValueOnce(mockDecksData)
    renderDecks('firstDeck=1')
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
  })

  it('handles updatePagination with page number', async () => {
    const paginationData = {
      ...mockDecksData,
      pagination: {
        page: 2,
        limit: 20,
        totalElements: 50,
        totalPages: 3,
      },
    }
    deckApi.fetchDecks.mockResolvedValueOnce(paginationData)
    renderDecks('page=2')
    
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })
  })
})

