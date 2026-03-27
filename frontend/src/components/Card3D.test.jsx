import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Card3D from './Card3D'

describe('Card3D', () => {
  const mockCard = {
    id: 1,
    name: 'Blue-Eyes White Dragon',
    type: 'Monster',
    attribute: 'Light',
    race: 'Dragon',
    level: 8,
    attackPoints: 3000,
    defensePoints: 2500,
    cost: 8,
    image: 'https://example.com/card.jpg',
  }

  it('renders card name', () => {
    render(<Card3D card={mockCard} />)
    expect(screen.getByText('Blue-Eyes White Dragon')).toBeInTheDocument()
  })

  it('renders card type', () => {
    render(<Card3D card={mockCard} />)
    expect(screen.getByText('Monster')).toBeInTheDocument()
  })

  it('renders card attribute', () => {
    render(<Card3D card={mockCard} />)
    expect(screen.getByText('Light')).toBeInTheDocument()
  })

  it('renders ATK/DEF in button for monsters', () => {
    render(<Card3D card={mockCard} />)
    expect(screen.getByText(/ATK 3000 \/ DEF 2500/)).toBeInTheDocument()
  })

  it('renders ? for variable ATK/DEF', () => {
    const variableCard = { ...mockCard, attackPoints: -1, defensePoints: -1 }
    render(<Card3D card={variableCard} />)
    expect(screen.getByText(/ATK \? \/ DEF \?/)).toBeInTheDocument()
  })

  it('renders race and level', () => {
    render(<Card3D card={mockCard} />)
    expect(screen.getByText('Dragon')).toBeInTheDocument()
    expect(screen.getByText(/Level: 8/)).toBeInTheDocument()
  })

  it('handles mouse events', () => {
    render(<Card3D card={mockCard} />)
    const cardElement = screen.getByText('Blue-Eyes White Dragon').closest('div')
    
    fireEvent.mouseEnter(cardElement)
    fireEvent.mouseMove(cardElement, { clientX: 100, clientY: 100 })
    fireEvent.mouseLeave(cardElement)
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Card3D card={mockCard} onClick={handleClick} />)
    const cardElement = screen.getByText('Blue-Eyes White Dragon').closest('div')
    
    fireEvent.click(cardElement)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('retries image load on error and shows fallback with label after max retries', async () => {
    const { rerender } = render(<Card3D card={mockCard} />)
    const getImg = () => screen.getByAltText('Blue-Eyes White Dragon')
    // First error triggers retry (retryCount 0 -> 1)
    fireEvent.error(getImg())
    await new Promise((r) => setTimeout(r, 450))
    // Second error triggers retry (retryCount 1 -> 2)
    fireEvent.error(getImg())
    await new Promise((r) => setTimeout(r, 450))
    // Third error triggers fallback
    fireEvent.error(getImg())
    expect(screen.getByText('Image not found')).toBeInTheDocument()
  })

  it('handles card without image', () => {
    const cardWithoutImage = { ...mockCard, image: null }
    render(<Card3D card={cardWithoutImage} />)
    expect(screen.getByAltText('Blue-Eyes White Dragon')).toBeInTheDocument()
  })

  it('handles spell card', () => {
    const spellCard = {
      ...mockCard,
      type: 'Spell',
      attribute: null,
      attackPoints: null,
      defensePoints: null,
    }
    render(<Card3D card={spellCard} />)
    expect(screen.getByText('Spell')).toBeInTheDocument()
    expect(screen.getByText(/— \/ —/)).toBeInTheDocument()
  })

  it('handles trap card', () => {
    const trapCard = {
      ...mockCard,
      type: 'Trap',
      attribute: null,
      attackPoints: null,
      defensePoints: null,
    }
    render(<Card3D card={trapCard} />)
    expect(screen.getByText('Trap')).toBeInTheDocument()
  })

  it('handles different attributes', () => {
    const attributes = ['Dark', 'Light', 'Earth', 'Water', 'Fire', 'Wind', 'Divine']
    attributes.forEach((attr) => {
      const { unmount } = render(<Card3D card={{ ...mockCard, attribute: attr }} />)
      expect(screen.getByText(attr)).toBeInTheDocument()
      unmount()
    })
  })

  it('handles card without attribute', () => {
    const cardWithoutAttr = { ...mockCard, attribute: null }
    render(<Card3D card={cardWithoutAttr} />)
    expect(screen.queryByText(/Light/)).not.toBeInTheDocument()
  })

  it('handles card without race', () => {
    const cardWithoutRace = { ...mockCard, race: null }
    render(<Card3D card={cardWithoutRace} />)
    expect(screen.queryByText(/Category:/)).not.toBeInTheDocument()
  })

  it('handles card with level 0', () => {
    const cardLevel0 = { ...mockCard, level: 0 }
    render(<Card3D card={cardLevel0} />)
    expect(screen.queryByText(/Level:/)).not.toBeInTheDocument()
  })

  it('handles unknown card type', () => {
    const unknownTypeCard = { ...mockCard, type: 'Unknown' }
    render(<Card3D card={unknownTypeCard} />)
    expect(screen.getByText('Unknown')).toBeInTheDocument()
  })
})

