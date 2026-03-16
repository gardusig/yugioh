import React, { useState, useEffect, useCallback } from 'react'
import { CARD_BACK_IMAGE, CARD_ARTWORK_CROP, IMAGE_NOT_FOUND_LABEL } from '../constants/cardImages'
import { getCardTypeTheme, getAttributeLabelColor, getRaceLabelColor } from '../constants/cardTypeTheme'

const IMAGE_LOAD_MAX_RETRIES = 3

function CardDetailModal({ card, onClose }) {
  const [showBack, setShowBack] = useState(false)
  const [imageError, setImageError] = useState(false)
  const [backImageError, setBackImageError] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  useEffect(() => {
    setImageError(false)
    setBackImageError(false)
    setRetryCount(0)
  }, [card?.id])

  const handleImageError = useCallback(() => {
    if (retryCount < IMAGE_LOAD_MAX_RETRIES - 1) {
      setTimeout(() => setRetryCount((c) => c + 1), 400)
    } else {
      setImageError(true)
    }
  }, [retryCount])

  const handleBackImageError = useCallback(() => {
    setBackImageError(true)
  }, [])

  if (!card) return null

  const theme = getCardTypeTheme(card.type)
  const attributeColor = card.attribute ? getAttributeLabelColor(card.attribute) : null
  const raceColor = getRaceLabelColor()
  const cardImage = imageError || !card.image ? CARD_BACK_IMAGE : card.image
  const displayImage = showBack ? CARD_BACK_IMAGE : cardImage
  const showNotFoundLabel = !showBack && imageError
  const showBackFallback = showBack && backImageError

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative bg-yugioh-dark rounded-xl shadow-2xl max-w-lg w-full overflow-hidden border-2"
        style={{ borderColor: theme.borderColor, boxShadow: theme.glow }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-gray-800 hover:bg-gray-700 text-white font-bold text-xl flex items-center justify-center transition-colors"
          aria-label="Close"
        >
          ×
        </button>

        {/* Card image area: frame background matches card type; image centered with border, shifted down */}
        <div className="relative">
          <div
            className="aspect-[421/614] max-h-[70vh] mx-auto flex items-end justify-center relative pt-4 pb-3 px-4"
            style={{ backgroundColor: theme.frameBg }}
          >
            {showBackFallback ? (
              <div
                className="w-full h-full flex items-center justify-center rounded-lg bg-gradient-to-br from-yugioh-dark via-[#1a1a2e] to-yugioh-dark border-2 border-black/25"
                aria-label="Card back"
              >
                <div className="text-center text-gray-500 text-sm font-medium px-4">
                  Card back
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center rounded-lg border-2 border-black/25 overflow-hidden bg-black/10">
                <div className="w-full h-full aspect-square max-w-full max-h-full rounded-md overflow-hidden">
                  <img
                    key={showBack ? 'back' : `${card.id}-${retryCount}`}
                    src={displayImage}
                    alt={showBack ? 'Card back' : card.name}
                    className="w-full h-full object-cover rounded-md"
                    style={{
                      objectPosition: showBack ? '50% 50%' : CARD_ARTWORK_CROP.objectPosition,
                    }}
                    onError={showBack ? handleBackImageError : handleImageError}
                  />
                </div>
              </div>
            )}
            {showNotFoundLabel && (
              <span
                className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-bold text-white bg-black/70 rounded px-2 py-1"
                aria-label={IMAGE_NOT_FOUND_LABEL}
              >
                {IMAGE_NOT_FOUND_LABEL}
              </span>
            )}
          </div>
          <button
            onClick={() => setShowBack(!showBack)}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg font-bold text-sm transition-colors"
          >
            {showBack ? 'Show front' : 'Show back'}
          </button>
        </div>

        {/* Card details */}
        <div className="p-6 border-t border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-3">{card.name}</h2>
          <div className="flex flex-col gap-2 mb-3">
            <span
              className="px-2 py-1 rounded text-xs font-bold w-fit"
              style={{ backgroundColor: theme.tagBgColor, color: theme.tagTextColor }}
            >
              {card.type}
            </span>
            <div className="flex flex-wrap gap-2">
              {card.attribute && attributeColor && (
                <span
                  className="px-2 py-1 rounded text-xs font-bold"
                  style={{ backgroundColor: attributeColor.bg, color: attributeColor.text }}
                >
                  {card.attribute}
                </span>
              )}
              {card.race && (
                <span
                  className="px-2 py-1 rounded text-xs font-bold"
                  style={{ backgroundColor: raceColor.bg, color: raceColor.text }}
                >
                  {card.race}
                </span>
              )}
            </div>
          </div>
          {card.type?.toLowerCase().includes('monster') && (
            <div className="text-gray-300 text-sm mb-3 px-3 py-2 rounded bg-gray-700/80">
              {card.level > 0 && <span>Level {card.level}</span>}
              <span className="mx-2">•</span>
              <span>
                ATK {card.attackPoints == null || card.attackPoints === -1 ? '?' : card.attackPoints} / DEF{' '}
                {card.defensePoints == null || card.defensePoints === -1 ? '?' : card.defensePoints}
              </span>
            </div>
          )}
          {card.description && (
            <p className="text-gray-400 text-sm leading-relaxed">{card.description}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default CardDetailModal
