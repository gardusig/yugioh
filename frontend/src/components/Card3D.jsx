import React, { useState, useEffect, useCallback } from 'react'
import { CARD_BACK_IMAGE, CARD_ARTWORK_CROP, IMAGE_NOT_FOUND_LABEL } from '../constants/cardImages'
import { getCardTypeTheme, getAttributeLabelColor, getRaceLabelColor } from '../constants/cardTypeTheme'

const IMAGE_LOAD_MAX_RETRIES = 3

function Card3D({ card, onClick }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const [imageError, setImageError] = useState(false)
  const [retryCount, setRetryCount] = useState(0)

  // Reset retry/error state when card changes so we always try the CSV image URL first
  useEffect(() => {
    setImageError(false)
    setRetryCount(0)
  }, [card?.id])

  const handleImageError = useCallback(() => {
    if (retryCount < IMAGE_LOAD_MAX_RETRIES - 1) {
      setTimeout(() => setRetryCount((c) => c + 1), 400)
    } else {
      setImageError(true)
    }
  }, [retryCount])

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateX = ((y - centerY) / centerY) * -10
    const rotateY = ((x - centerX) / centerX) * 10

    setMousePosition({ x: rotateX, y: rotateY })
  }

  const handleMouseEnter = () => {
    setIsHovered(true)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    setMousePosition({ x: 0, y: 0 })
  }

  const cardStyle = {
    transform: isHovered
      ? `perspective(1000px) rotateX(${mousePosition.x}deg) rotateY(${mousePosition.y}deg) translateZ(30px)`
      : 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)',
    transition: isHovered ? 'none' : 'transform 0.3s ease',
  }

  const theme = getCardTypeTheme(card?.type)

  const attributeStyle = card?.attribute ? getAttributeLabelColor(card.attribute) : null
  const raceStyle = getRaceLabelColor()

  return (
    <div
      className="relative cursor-pointer"
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={cardStyle}
    >
      <div
        className="relative w-64 h-96 bg-gradient-to-br from-yugioh-dark via-gray-900 to-yugioh-dark rounded-lg border-2 overflow-hidden transition-all"
        style={{
          borderColor: isHovered ? theme.borderColor : `${theme.borderColor}80`,
          boxShadow: isHovered ? theme.glow : '0 0 12px rgba(0,0,0,0.3)',
        }}
      >
        {/* Card Image Area: frame background matches card type; crop to artwork (cartoon) only */}
        <div
          className="h-48 flex items-end justify-center relative pt-2 pb-1 px-2"
          style={{ backgroundColor: theme.frameBg }}
        >
          <div className="w-full h-full flex items-center justify-center rounded border-2 border-black/25 overflow-hidden bg-black/10">
            <div className="w-full h-full aspect-square max-w-full max-h-full rounded overflow-hidden">
              <img
                key={`${card.id}-${retryCount}`}
                src={imageError || !card.image ? CARD_BACK_IMAGE : card.image}
                alt={card.name}
                className="w-full h-full object-cover"
                style={{ objectPosition: CARD_ARTWORK_CROP.objectPosition }}
                onError={handleImageError}
              />
            </div>
          </div>
          {imageError && (
            <span
              className="absolute bottom-1 left-1 right-1 text-center text-[10px] font-bold text-white bg-black/70 rounded px-1 py-0.5"
              aria-label={IMAGE_NOT_FOUND_LABEL}
            >
              {IMAGE_NOT_FOUND_LABEL}
            </span>
          )}
        </div>

        {/* Card Info */}
        <div className="p-4 h-48 flex flex-col">
          <div className="flex flex-col gap-2 mb-2">
            <span
              className="px-2 py-1 rounded text-xs font-bold w-fit"
              style={{ backgroundColor: theme.tagBgColor, color: theme.tagTextColor }}
            >
              {card.type}
            </span>
            <div className="flex flex-wrap gap-2">
              {card.attribute && (
                <span
                  className="px-2 py-1 rounded text-xs font-bold"
                  style={{ backgroundColor: attributeStyle.bg, color: attributeStyle.text }}
                >
                  {card.attribute}
                </span>
              )}
              {card.race && (
                <span
                  className="px-2 py-1 rounded text-xs font-bold"
                  style={{ backgroundColor: raceStyle.bg, color: raceStyle.text }}
                >
                  {card.race}
                </span>
              )}
            </div>
          </div>

          <h3 className="font-bold text-lg mb-2 text-white line-clamp-2">
            {card.name}
          </h3>

          <div className="mt-auto flex items-end justify-between gap-2">
            <div className="text-[10px] text-gray-400 leading-tight min-w-0">
              {card.level > 0 && <div>Level: {card.level}</div>}
            </div>
            <div className="bg-gray-600 text-white px-2 py-0.5 rounded-full font-bold text-[10px] whitespace-nowrap shrink-0">
              {card.type?.toLowerCase().includes('monster')
                ? `ATK ${card.attackPoints == null || card.attackPoints === -1 ? '?' : card.attackPoints} / DEF ${card.defensePoints == null || card.defensePoints === -1 ? '?' : card.defensePoints}`
                : '— / —'}
            </div>
          </div>
        </div>

        {/* Glow effect on hover — matches card type color */}
        {isHovered && (
          <div
            className="absolute inset-0 pointer-events-none rounded-lg opacity-20"
            style={{
              background: `linear-gradient(to bottom right, ${theme.borderColor}, transparent)`,
            }}
          />
        )}
      </div>
    </div>
  )
}

export default Card3D

