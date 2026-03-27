/**
 * Card back image - official Yu-Gi-Oh! OCG/TCG style.
 * Used as fallback when the card image URL (e.g. from CSV) fails after retries.
 * Japanese OCG back (widely used, reliable CDN).
 */
export const CARD_BACK_IMAGE =
  'https://static.wikia.nocookie.net/yugioh/images/d/da/Back-JP.png/revision/latest?cb=20100726082049'

/** Label shown when the card image could not be loaded after retries. */
export const IMAGE_NOT_FOUND_LABEL = 'Image not found'

/**
 * Artwork crop: focus the preview on the card's illustration (the "cartoon" area).
 * - Standard card layout: name/stars top ~18%, artwork middle ~18–62%, text/ATK-DEF bottom ~62%+.
 * - We trim lateral borders (object-fit: cover in a square crops left/right) and center
 *   vertically on the artwork band (object-position Y).
 * Values as CSS object-position percentages: [x, y]. Center of artwork ≈ (50%, 40%).
 */
export const CARD_ARTWORK_CROP = {
  objectPosition: '50% 40%',
  /** Use with a square or near-square container + object-fit: cover to show only the artwork. */
  objectFit: 'cover',
}
