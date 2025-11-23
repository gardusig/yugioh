import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DeckDetail from './DeckDetail'
import * as deckApi from '../api/deckApi'

// Mock the API module
vi.mock('../api/deckApi')

describe('DeckDetail', () => {
  const mockDeckData = {
    id: 1,
    name: 'Yugi Deck',
    description: 'Yugi Muto deck',
    characterName: 'Yugi Muto',
    archetype: 'Spellcaster',
    mostCommonType: 'Dark',
    totalCost: 200,
    maxCost: 250,
    isPreset: true,
    cards: [
      {
        id: 1,
        name: 'Dark Magician',
        type: 'Monster',
        attribute: 'Dark',
        attackPoints: 2500,
        defensePoints: 2100,
        cost: 7,
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock implementation
    deckApi.fetchDeckById.mockResolvedValue(mockDeckData)
  })

  const renderDeckDetail = (deckId = '1') => {
    const Wrapper = ({ children }) => (
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/decks/:id" element={children} />
        </Routes>
      </BrowserRouter>
    )
    window.history.pushState({}, '', `/decks/${deckId}`)
    return render(<DeckDetail />, { wrapper: Wrapper })
  }

  it('renders loading state initially', () => {
    deckApi.fetchDeckById.mockImplementation(() => new Promise(() => {})) // Never resolves
    renderDeckDetail()
    expect(screen.getByText('Loading deck...')).toBeInTheDocument()
  })

  it('fetches and displays deck', async () => {
    deckApi.fetchDeckById.mockResolvedValueOnce(mockDeckData)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
    // Character name is displayed as "Character: Yugi Muto", so use a flexible matcher
    // There might be multiple instances, so use getAllByText
    expect(screen.getAllByText(/Yugi Muto/).length).toBeGreaterThan(0)
    expect(screen.getByText('Spellcaster')).toBeInTheDocument()
    expect(deckApi.fetchDeckById).toHaveBeenCalledWith(1)
  })

  it('displays deck cards', async () => {
    deckApi.fetchDeckById.mockResolvedValueOnce(mockDeckData)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Dark Magician')).toBeInTheDocument()
    })
  })

  it('displays preset badge', async () => {
    deckApi.fetchDeckById.mockResolvedValueOnce(mockDeckData)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Preset Deck')).toBeInTheDocument()
    })
  })

  it('displays cost information', async () => {
    deckApi.fetchDeckById.mockResolvedValueOnce(mockDeckData)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText(/200\/250/)).toBeInTheDocument()
      expect(screen.getByText(/1\/40/)).toBeInTheDocument()
    })
  })

  it('handles deck not found', async () => {
    deckApi.fetchDeckById.mockResolvedValueOnce(null)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Deck not found')).toBeInTheDocument()
    })
  })

  it('handles fetch error', async () => {
    deckApi.fetchDeckById.mockRejectedValueOnce(new Error('Network error'))
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.queryByText('Loading deck...')).not.toBeInTheDocument()
    })
  })

  it('handles deck without cards', async () => {
    const deckWithoutCards = {
      ...mockDeckData,
      cards: [],
    }
    deckApi.fetchDeckById.mockResolvedValueOnce(deckWithoutCards)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('No cards in this deck')).toBeInTheDocument()
    })
  })

  it('handles deck without description', async () => {
    const deckWithoutDesc = {
      ...mockDeckData,
      description: null,
    }
    deckApi.fetchDeckById.mockResolvedValueOnce(deckWithoutDesc)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
  })

  it('handles deck without character name', async () => {
    const deckWithoutChar = {
      ...mockDeckData,
      characterName: null,
    }
    deckApi.fetchDeckById.mockResolvedValueOnce(deckWithoutChar)
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
  })

})

