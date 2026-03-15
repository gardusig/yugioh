import React, { useState } from 'react'
import { CARD_BACK_IMAGE } from '../constants/cardImages'

function Card3D({ card, onClick }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const [imageError, setImageError] = useState(false)

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

  const getAttributeColor = (attribute) => {
    const colors = {
      'Dark': 'bg-gray-800',
      'Light': 'bg-yellow-300 text-gray-900',
      'Earth': 'bg-amber-700',
      'Water': 'bg-blue-500',
      'Fire': 'bg-red-600',
      'Wind': 'bg-green-500',
      'Divine': 'bg-purple-500',
    }
    return colors[attribute] || 'bg-gray-600'
  }

  const getTypeColor = (type) => {
    if (!type) return 'bg-gray-600'
    const t = type.toLowerCase()
    if (t.includes('monster')) return 'bg-red-600'
    if (t.includes('spell')) return 'bg-green-600'
    if (t.includes('trap')) return 'bg-pink-600'
    return 'bg-gray-600'
  }

  return (
    <div
      className="relative cursor-pointer"
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={cardStyle}
    >
      <div className="relative w-64 h-96 bg-gradient-to-br from-yugioh-dark via-gray-900 to-yugioh-dark rounded-lg shadow-card-glow border-2 border-yugioh-accent/50 overflow-hidden hover:border-yugioh-accent hover:shadow-yugioh-glow transition-all">
        {/* Card Image Area */}
        <div className="h-48 bg-gray-700 flex items-center justify-center">
          <img 
            src={imageError || !card.image ? CARD_BACK_IMAGE : card.image} 
            alt={card.name}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />
        </div>

        {/* Card Info */}
        <div className="p-4 h-48 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <span className={`px-2 py-1 rounded text-xs font-bold ${getTypeColor(card.type)}`}>
              {card.type}
            </span>
            {card.attribute && (
              <span className={`px-2 py-1 rounded text-xs font-bold ${getAttributeColor(card.attribute)}`}>
                {card.attribute}
              </span>
            )}
          </div>

          <h3 className="font-bold text-lg mb-2 text-white line-clamp-2">
            {card.name}
          </h3>

          <div className="mt-auto flex items-end justify-between gap-2">
            <div className="text-[10px] text-gray-400 leading-tight min-w-0">
              {card.race && <div>Category: {card.race}</div>}
              {card.level > 0 && <div>Level: {card.level}</div>}
            </div>
            <div className="bg-yugioh-accent text-yugioh-dark px-2 py-0.5 rounded-full font-bold text-[10px] whitespace-nowrap shadow-lg shrink-0">
              {card.type?.toLowerCase().includes('monster')
                ? `ATK ${card.attackPoints == null || card.attackPoints === -1 ? '?' : card.attackPoints} / DEF ${card.defensePoints == null || card.defensePoints === -1 ? '?' : card.defensePoints}`
                : '— / —'}
            </div>
          </div>
        </div>

        {/* Glow effect on hover */}
        {isHovered && (
          <div className="absolute inset-0 bg-gradient-to-br from-yugioh-accent/20 via-yugioh-accent/10 to-transparent pointer-events-none rounded-lg" />
        )}
      </div>
    </div>
  )
}

export default Card3D

