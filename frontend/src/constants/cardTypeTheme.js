/**
 * Card type → border, glow, tag, and frame colors (Yu-Gi-Oh! frame colors).
 * Uses hex colors so styles work without relying on Tailwind class purging.
 */
const TYPE_THEMES = {
  // Normal Monster: yellow/beige (vanilla card frame)
  normal: {
    borderColor: '#c9a227',
    glow: '0 0 20px rgba(201, 162, 39, 0.5), 0 0 40px rgba(201, 162, 39, 0.25)',
    tagBgColor: '#d4af37',
    tagTextColor: '#1a1a1a',
    frameBg: '#e8d5a3', // light yellow/beige like Normal Monster frame
  },
  // Effect Monster: reddish-brown / burnt orange (#BB5D39)
  effect: {
    borderColor: '#BB5D39',
    glow: '0 0 20px rgba(187, 93, 57, 0.5), 0 0 40px rgba(187, 93, 57, 0.25)',
    tagBgColor: '#BB5D39',
    tagTextColor: '#ffffff',
    frameBg: '#c96b45',
  },
  // Fusion: purple
  fusion: {
    borderColor: '#7b1fa2',
    glow: '0 0 20px rgba(123, 31, 162, 0.5), 0 0 40px rgba(123, 31, 162, 0.25)',
    tagBgColor: '#7b1fa2',
    tagTextColor: '#ffffff',
    frameBg: '#9c27b0',
  },
  // Ritual: blue
  ritual: {
    borderColor: '#1565c0',
    glow: '0 0 20px rgba(21, 101, 192, 0.5), 0 0 40px rgba(21, 101, 192, 0.25)',
    tagBgColor: '#1565c0',
    tagTextColor: '#ffffff',
    frameBg: '#1976d2',
  },
  // Synchro: white/light
  synchro: {
    borderColor: '#e0e0e0',
    glow: '0 0 20px rgba(224, 224, 224, 0.5), 0 0 40px rgba(224, 224, 224, 0.2)',
    tagBgColor: '#e0e0e0',
    tagTextColor: '#212121',
    frameBg: '#f5f5f5',
  },
  // XYZ: black/dark
  xyz: {
    borderColor: '#37474f',
    glow: '0 0 20px rgba(55, 71, 79, 0.6), 0 0 40px rgba(55, 71, 79, 0.3)',
    tagBgColor: '#37474f',
    tagTextColor: '#eceff1',
    frameBg: '#455a64',
  },
  // Link: blue
  link: {
    borderColor: '#0277bd',
    glow: '0 0 20px rgba(2, 119, 189, 0.5), 0 0 40px rgba(2, 119, 189, 0.25)',
    tagBgColor: '#0277bd',
    tagTextColor: '#ffffff',
    frameBg: '#0288d1',
  },
  // Spell: green
  spell: {
    borderColor: '#2e7d32',
    glow: '0 0 20px rgba(46, 125, 50, 0.5), 0 0 40px rgba(46, 125, 50, 0.25)',
    tagBgColor: '#2e7d32',
    tagTextColor: '#ffffff',
    frameBg: '#388e3c',
  },
  // Trap: pink
  trap: {
    borderColor: '#c2185b',
    glow: '0 0 20px rgba(194, 24, 91, 0.5), 0 0 40px rgba(194, 24, 91, 0.25)',
    tagBgColor: '#c2185b',
    tagTextColor: '#ffffff',
    frameBg: '#e91e63',
  },
}

const DEFAULT_THEME = {
  borderColor: '#6b7280',
  glow: '0 0 20px rgba(107, 114, 128, 0.4), 0 0 40px rgba(107, 114, 128, 0.2)',
  tagBgColor: '#4b5563',
  tagTextColor: '#ffffff',
  frameBg: '#4b5563',
}

/**
 * Attribute → label colors (Yu-Gi-Oh! OCG/TCG attribute icon conventions).
 * Key is lowercase; pass attribute with any casing.
 */
const ATTRIBUTE_COLORS = {
  dark: { bg: '#37474f', text: '#eceff1' },       // dark gray/slate (DARK icon)
  light: { bg: '#ffb300', text: '#1a1a1a' },      // amber/gold (LIGHT icon)
  earth: { bg: '#6d4c41', text: '#fff8e1' },      // brown (EARTH icon)
  fire: { bg: '#bf360c', text: '#ffffff' },        // deep orange-red (FIRE icon)
  water: { bg: '#0277bd', text: '#ffffff' },       // blue (WATER icon)
  wind: { bg: '#558b2f', text: '#ffffff' },        // green (WIND icon)
  divine: { bg: '#7b1fa2', text: '#ffffff' },      // purple (DIVINE)
}
const DEFAULT_ATTRIBUTE_COLOR = { bg: '#546e7a', text: '#ffffff' }

/** Race (Type/Category) label: single neutral color so Attribute stands out. */
const RACE_LABEL_COLOR = { bg: '#455a64', text: '#eceff1' }

/**
 * @param {string} attribute - e.g. "DARK", "Light"
 * @returns {{ bg: string, text: string }}
 */
export function getAttributeLabelColor(attribute) {
  if (!attribute) return DEFAULT_ATTRIBUTE_COLOR
  const key = String(attribute).toLowerCase()
  return ATTRIBUTE_COLORS[key] ?? DEFAULT_ATTRIBUTE_COLOR
}

/**
 * @returns {{ bg: string, text: string }}
 */
export function getRaceLabelColor() {
  return RACE_LABEL_COLOR
}

/**
 * @param {string} type - Card type (e.g. "Normal Monster", "Effect Monster", "Spell Card")
 * @returns {{ borderColor: string, glow: string, tagBgColor: string, tagTextColor: string, frameBg: string }}
 */
export function getCardTypeTheme(type) {
  if (!type) return DEFAULT_THEME
  const t = type.toLowerCase()
  if (t.includes('normal') && t.includes('monster')) return TYPE_THEMES.normal
  if (t.includes('effect') && t.includes('monster')) return TYPE_THEMES.effect
  if (t.includes('fusion')) return TYPE_THEMES.fusion
  if (t.includes('ritual')) return TYPE_THEMES.ritual
  if (t.includes('synchro')) return TYPE_THEMES.synchro
  if (t.includes('xyz')) return TYPE_THEMES.xyz
  if (t.includes('link')) return TYPE_THEMES.link
  if (t.includes('spell')) return TYPE_THEMES.spell
  if (t.includes('trap')) return TYPE_THEMES.trap
  // Generic "Monster" (e.g. token) → effect-like
  if (t.includes('monster')) return TYPE_THEMES.effect
  return DEFAULT_THEME
}
