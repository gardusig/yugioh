import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  const renderApp = () => {
    // App already contains a Router, so we don't need to wrap it
    return render(<App />)
  }

  it('renders navigation', () => {
    renderApp()
    // Text appears in both nav and home page, so use getAllByText
    expect(screen.getAllByText(/Yu-Gi-Oh! The Sacred Cards/).length).toBeGreaterThan(0)
    expect(screen.getByText('Cards')).toBeInTheDocument()
    expect(screen.getByText('Decks')).toBeInTheDocument()
  })

  it('renders home page', () => {
    renderApp()
    expect(screen.getByText(/Welcome to Yu-Gi-Oh! The Sacred Cards/)).toBeInTheDocument()
    expect(screen.getByText('View Cards')).toBeInTheDocument()
    expect(screen.getByText('View Decks')).toBeInTheDocument()
  })

  it('renders home page description', () => {
    renderApp()
    expect(screen.getByText(/Browse all 900 cards and explore character decks/)).toBeInTheDocument()
  })
})

