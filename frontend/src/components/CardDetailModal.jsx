import React, { useState, useEffect } from 'react'
import { CARD_BACK_IMAGE } from '../constants/cardImages'

function CardDetailModal({ card, onClose }) {
  const [showBack, setShowBack] = useState(false)

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  if (!card) return null

  const cardImage = card.image || CARD_BACK_IMAGE
  const displayImage = showBack ? CARD_BACK_IMAGE : cardImage

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative bg-yugioh-dark border-2 border-yugioh-accent rounded-xl shadow-2xl max-w-lg w-full overflow-hidden"
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

        {/* Card image area with flip toggle */}
        <div className="relative">
          <div className="aspect-[421/614] max-h-[70vh] mx-auto flex items-center justify-center bg-gray-900">
            <img
              src={displayImage}
              alt={showBack ? 'Card back' : card.name}
              className="max-h-full w-auto object-contain rounded-lg"
            />
          </div>
          <button
            onClick={() => setShowBack(!showBack)}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-yugioh-accent text-yugioh-dark rounded-lg font-bold text-sm hover:bg-yugioh-gold transition-colors"
          >
            {showBack ? 'Show front' : 'Show back'}
          </button>
        </div>

        {/* Card details */}
        <div className="p-6 border-t border-yugioh-accent/30">
          <h2 className="text-2xl font-bold text-white mb-3">{card.name}</h2>
          <div className="flex flex-wrap gap-2 mb-3">
            <span className="px-2 py-1 rounded text-xs font-bold bg-gray-600 text-white">
              {card.type}
            </span>
            {card.attribute && (
              <span className="px-2 py-1 rounded text-xs font-bold bg-gray-600 text-white">
                {card.attribute}
              </span>
            )}
            {card.race && (
              <span className="px-2 py-1 rounded text-xs font-bold bg-gray-600 text-white">
                {card.race}
              </span>
            )}
          </div>
          {card.type?.toLowerCase().includes('monster') && (
            <div className="text-gray-300 text-sm mb-3">
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
