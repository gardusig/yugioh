import { getApiUrl } from './config'

/**
 * Fetch cards with pagination
 * @param {Object} params - Query parameters
 * @param {number} [params.page] - Page number (1-based)
 * @param {number} [params.firstCard] - First card ID to start from
 * @param {number} [params.limit=24] - Number of cards per page
 * @returns {Promise<{cards: Array, pagination: Object}>}
 */
export const fetchCards = async ({ page, firstCard, limit = 24 } = {}) => {
  const params = new URLSearchParams()
  
  if (firstCard) {
    params.append('firstCard', firstCard)
  } else if (page) {
    params.append('page', page)
  } else {
    params.append('page', '1')
  }
  params.append('limit', limit.toString())

  const response = await fetch(getApiUrl(`/cards?${params.toString()}`))
  
  if (!response.ok) {
    throw new Error(`Failed to fetch cards: ${response.statusText}`)
  }
  
  const data = await response.json()
  return {
    cards: data.cards || [],
    pagination: data.pagination,
  }
}

/**
 * Fetch a single card by ID
 * @param {number} id - Card ID
 * @returns {Promise<Object>}
 */
export const fetchCardById = async (id) => {
  const response = await fetch(getApiUrl(`/cards/${id}`))
  
  if (!response.ok) {
    throw new Error(`Failed to fetch card: ${response.statusText}`)
  }
  
  return response.json()
}

