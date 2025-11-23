import { getApiUrl } from './config'

/**
 * Fetch decks with pagination and filters
 * @param {Object} params - Query parameters
 * @param {number} [params.page] - Page number (1-based)
 * @param {number} [params.firstDeck] - First deck ID to start from
 * @param {number} [params.limit=20] - Number of decks per page
 * @param {string} [params.archetype] - Filter by archetype
 * @param {boolean} [params.preset] - Filter preset decks only
 * @returns {Promise<{decks: Array, pagination: Object}>}
 */
export const fetchDecks = async ({ page, firstDeck, limit = 20, archetype, preset } = {}) => {
  const params = new URLSearchParams()
  
  if (firstDeck) {
    params.append('firstDeck', firstDeck)
  } else if (page) {
    params.append('page', page)
  } else {
    params.append('page', '1')
  }
  params.append('limit', limit.toString())
  
  if (archetype) {
    params.append('archetype', archetype)
  }
  if (preset !== undefined) {
    params.append('preset', preset.toString())
  }

  const response = await fetch(getApiUrl(`/decks?${params.toString()}`))
  
  if (!response.ok) {
    throw new Error(`Failed to fetch decks: ${response.statusText}`)
  }
  
  const data = await response.json()
  return {
    decks: data.decks || [],
    pagination: data.pagination,
  }
}

/**
 * Fetch a single deck by ID with all cards
 * @param {number} id - Deck ID
 * @returns {Promise<Object>}
 */
export const fetchDeckById = async (id) => {
  const response = await fetch(getApiUrl(`/decks/${id}`))
  
  if (!response.ok) {
    if (response.status === 404) {
      return null
    }
    throw new Error(`Failed to fetch deck: ${response.statusText}`)
  }
  
  return response.json()
}

