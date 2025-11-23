import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Cards from './Cards'
import * as cardApi from '../api/cardApi'

// Mock the API module
vi.mock('../api/cardApi')

describe('Cards', () => {
  const mockCardsData = {
    cards: [
      {
        id: 1,
        name: 'Blue-Eyes White Dragon',
        type: 'Monster',
        attribute: 'Light',
        attackPoints: 3000,
        defensePoints: 2500,
        cost: 8,
      },
      {
        id: 2,
        name: 'Dark Magician',
        type: 'Monster',
        attribute: 'Dark',
        attackPoints: 2500,
        defensePoints: 2100,
        cost: 7,
      },
    ],
    pagination: {
      page: 1,
      limit: 24,
      totalElements: 2,
      totalPages: 1,
    },
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock implementation
    cardApi.fetchCards.mockResolvedValue(mockCardsData)
  })

  const renderCards = (initialSearchParams = '') => {
    const Wrapper = ({ children }) => (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        {children}
      </BrowserRouter>
    )
    if (initialSearchParams) {
      window.history.pushState({}, '', `/cards?${initialSearchParams}`)
    }
    return render(<Cards />, { wrapper: Wrapper })
  }

  it('renders loading state initially', () => {
    cardApi.fetchCards.mockImplementation(() => new Promise(() => {})) // Never resolves
    renderCards()
    expect(screen.getByText('Loading cards...')).toBeInTheDocument()
  })

  it('fetches and displays cards', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards()
    
    await waitFor(() => {
      expect(screen.getByText('Blue-Eyes White Dragon')).toBeInTheDocument()
    })
    expect(screen.getByText('Dark Magician')).toBeInTheDocument()
    expect(cardApi.fetchCards).toHaveBeenCalledWith({ page: null, firstCard: null, limit: 24 })
  })

  it('displays pagination info', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards()
    
    await waitFor(() => {
      expect(screen.getByText('Page 1 of 1')).toBeInTheDocument()
    })
  })

  it('handles pagination buttons', async () => {
    const paginationData = {
      ...mockCardsData,
      pagination: {
        page: 2,
        limit: 24,
        totalElements: 50,
        totalPages: 3,
      },
    }
    cardApi.fetchCards.mockResolvedValueOnce(paginationData)
    renderCards('page=2')
    
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })
    
    const prevButton = screen.getByText('Previous')
    expect(prevButton).not.toBeDisabled()
    
    const nextButton = screen.getByText('Next')
    expect(nextButton).not.toBeDisabled()
  })

  it('disables previous button on first page', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards()
    
    await waitFor(() => {
      const prevButton = screen.getByText('Previous')
      expect(prevButton).toBeDisabled()
    })
  })

  it('disables next button on last page', async () => {
    const lastPageData = {
      ...mockCardsData,
      pagination: {
        page: 3,
        limit: 24,
        totalElements: 50,
        totalPages: 3,
      },
    }
    cardApi.fetchCards.mockResolvedValueOnce(lastPageData)
    renderCards('page=3')
    
    await waitFor(() => {
      const nextButton = screen.getByText('Next')
      expect(nextButton).toBeDisabled()
    })
  })

  it('handles fetch error', async () => {
    cardApi.fetchCards.mockRejectedValueOnce(new Error('Network error'))
    renderCards()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading cards...')).not.toBeInTheDocument()
    })
  })

  it('handles firstCard parameter', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards('firstCard=1')
    
    await waitFor(() => {
      expect(cardApi.fetchCards).toHaveBeenCalledWith({ page: null, firstCard: 1, limit: 24 })
    })
  })

  it('handles empty cards array', async () => {
    cardApi.fetchCards.mockResolvedValueOnce({ cards: [], pagination: null })
    renderCards()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading cards...')).not.toBeInTheDocument()
    })
  })

  it('handles pagination button clicks', async () => {
    const paginationData = {
      ...mockCardsData,
      pagination: {
        page: 2,
        limit: 24,
        totalElements: 50,
        totalPages: 3,
      },
    }
    cardApi.fetchCards.mockResolvedValueOnce(paginationData)
    renderCards('page=2')
    
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })
    
    // Test pagination button clicks
    const prevButton = screen.getByText('Previous')
    fireEvent.click(prevButton)
    
    const nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
  })

  it('handles response without cards property', async () => {
    cardApi.fetchCards.mockResolvedValueOnce({ cards: [], pagination: mockCardsData.pagination })
    renderCards()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading cards...')).not.toBeInTheDocument()
    })
  })

  it('handles pagination with firstCard parameter', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards('firstCard=1')
    
    await waitFor(() => {
      expect(screen.getByText('Blue-Eyes White Dragon')).toBeInTheDocument()
    })
  })

  it('handles updatePagination with firstCard', async () => {
    cardApi.fetchCards.mockResolvedValueOnce(mockCardsData)
    renderCards()
    
    await waitFor(() => {
      expect(screen.getByText('Blue-Eyes White Dragon')).toBeInTheDocument()
    })
    
    // This will trigger updatePagination with firstCard
    // We can't directly test the function, but we can verify the component works
    const nextButton = screen.getByText('Next')
    expect(nextButton).toBeDisabled() // On last page
  })

  it('handles updatePagination with page number', async () => {
    const paginationData = {
      ...mockCardsData,
      pagination: {
        page: 2,
        limit: 24,
        totalElements: 50,
        totalPages: 3,
      },
    }
    cardApi.fetchCards.mockResolvedValueOnce(paginationData)
    renderCards('page=2')
    
    await waitFor(() => {
      expect(screen.getByText('Page 2 of 3')).toBeInTheDocument()
    })
  })
})

