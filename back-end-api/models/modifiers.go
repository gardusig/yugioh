package models

// LevelUpMultiplierMapper holds the level-up stat multipliers for each role
type LevelUpMultiplierMapper struct {
	strengthMultipliers     map[Role]float64
	dexterityMultipliers    map[Role]float64
	intelligenceMultipliers map[Role]float64
}

var levelUpMapper *LevelUpMultiplierMapper

// init initializes the level-up multiplier mapper
func init() {
	levelUpMapper = &LevelUpMultiplierMapper{
		strengthMultipliers: map[Role]float64{
			RoleWarrior: 0.80, // +80% of strength
			RoleThief:   0.25, // +25% of strength
			RoleMage:    0.20, // +20% of strength
		},
		dexterityMultipliers: map[Role]float64{
			RoleWarrior: 0.20, // +20% of dexterity
			RoleThief:   1.00, // +100% of dexterity
			RoleMage:    0.20, // +20% of dexterity
		},
		intelligenceMultipliers: map[Role]float64{
			RoleWarrior: 0.00, // No intelligence boost
			RoleThief:   0.25, // +25% of intelligence
			RoleMage:    1.20, // +120% of intelligence
		},
	}
}

// GetLevelUpMultipliers returns the stat multipliers for level-up based on role
func GetLevelUpMultipliers(role Role) (strengthMultiplier, dexterityMultiplier, intelligenceMultiplier float64) {
	strMult, ok := levelUpMapper.strengthMultipliers[role]
	if !ok {
		strMult = 0.0
	}

	dexMult, ok := levelUpMapper.dexterityMultipliers[role]
	if !ok {
		dexMult = 0.0
	}

	intMult, ok := levelUpMapper.intelligenceMultipliers[role]
	if !ok {
		intMult = 0.0
	}

	return strMult, dexMult, intMult
}

// GetStrengthMultiplier returns the strength multiplier for level-up
func GetStrengthMultiplier(role Role) float64 {
	mod, ok := levelUpMapper.strengthMultipliers[role]
	if !ok {
		return 0.0
	}
	return mod
}

// GetDexterityMultiplier returns the dexterity multiplier for level-up
func GetDexterityMultiplier(role Role) float64 {
	mod, ok := levelUpMapper.dexterityMultipliers[role]
	if !ok {
		return 0.0
	}
	return mod
}

// GetIntelligenceMultiplier returns the intelligence multiplier for level-up
func GetIntelligenceMultiplier(role Role) float64 {
	mod, ok := levelUpMapper.intelligenceMultipliers[role]
	if !ok {
		return 0.0
	}
	return mod
}

// GetSpeedModifier calculates the speed modifier for battle purposes based on role and stats
func GetSpeedModifier(role Role, dexterity, strength, intelligence int) float64 {
	switch role {
	case RoleWarrior:
		// Warrior: +60% of dexterity + 20% of intelligence
		return (float64(dexterity) * 0.60) + (float64(intelligence) * 0.20)
	case RoleThief:
		// Thief: +80% of dexterity
		return float64(dexterity) * 0.80
	case RoleMage:
		// Mage: +40% of dexterity + 10% of strength
		return (float64(dexterity) * 0.40) + (float64(strength) * 0.10)
	default:
		return 0.0
	}
}
