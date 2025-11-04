package models

// Role represents the character's role
type Role string

const (
	RoleWarrior Role = "Warrior"
	RoleThief   Role = "Thief"
	RoleMage    Role = "Mage"
)

// IsValidRole checks if a role is valid
func IsValidRole(role Role) bool {
	return role == RoleWarrior || role == RoleThief || role == RoleMage
}
