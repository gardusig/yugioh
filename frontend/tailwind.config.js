/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        yugioh: {
          dark: '#0a0e27',      // Deep navy blue (classic card back)
          purple: '#2d1b4e',    // Mystical purple
          blue: '#1a237e',      // Deep blue
          accent: '#FFD700',    // Classic gold/yellow
          gold: '#FFD700',      // Gold accent
          red: '#c62828',       // Monster red
          green: '#2e7d32',     // Spell green
          pink: '#c2185b',      // Trap pink
        },
      },
      backgroundImage: {
        'yugioh-gradient': 'linear-gradient(135deg, #0a0e27 0%, #1a237e 50%, #2d1b4e 100%)',
        'card-glow': 'radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%)',
      },
      boxShadow: {
        'yugioh-glow': '0 0 20px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.3)',
        'card-glow': '0 0 15px rgba(255, 215, 0, 0.4)',
      },
    },
  },
  plugins: [],
}

