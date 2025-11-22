import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DeckDetail from './DeckDetail'

// Mock fetch
global.fetch = vi.fn()

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
  })

  const renderDeckDetail = (deckId = '1') => {
    const Wrapper = ({ children }) => (
      <BrowserRouter>
        <Routes>
          <Route path="/decks/:id" element={children} />
        </Routes>
      </BrowserRouter>
    )
    window.history.pushState({}, '', `/decks/${deckId}`)
    return render(<DeckDetail />, { wrapper: Wrapper })
  }

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})) // Never resolves
    renderDeckDetail()
    expect(screen.getByText('Loading deck...')).toBeInTheDocument()
  })

  it('fetches and displays deck', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeckData,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
    // Character name is displayed as "Character: Yugi Muto", so use a flexible matcher
    // There might be multiple instances, so use getAllByText
    expect(screen.getAllByText(/Yugi Muto/).length).toBeGreaterThan(0)
    expect(screen.getByText('Spellcaster')).toBeInTheDocument()
  })

  it('displays deck cards', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeckData,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Dark Magician')).toBeInTheDocument()
    })
  })

  it('displays preset badge', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeckData,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Preset Deck')).toBeInTheDocument()
    })
  })

  it('displays cost information', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeckData,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText(/200\/250/)).toBeInTheDocument()
      expect(screen.getByText(/1\/40/)).toBeInTheDocument()
    })
  })

  it('handles deck not found', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Deck not found')).toBeInTheDocument()
    })
  })

  it('handles fetch error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))
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
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => deckWithoutCards,
    })
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
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => deckWithoutDesc,
    })
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
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => deckWithoutChar,
    })
    renderDeckDetail()
    
    await waitFor(() => {
      expect(screen.getByText('Yugi Deck')).toBeInTheDocument()
    })
  })

})

