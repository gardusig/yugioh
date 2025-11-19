package database

import (
	"embed"
	"fmt"
	"io/fs"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

// RunMigrations executes all migration files in order
func RunMigrations() error {
	if DB == nil {
		return fmt.Errorf("database connection not established")
	}

	// Read all migration files
	files, err := migrationsFS.ReadDir("migrations")
	if err != nil {
		return fmt.Errorf("failed to read migrations directory: %w", err)
	}

	// Sort files by number prefix
	migrationFiles := make([]fs.DirEntry, 0)
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".sql") {
			migrationFiles = append(migrationFiles, file)
		}
	}

	sort.Slice(migrationFiles, func(i, j int) bool {
		numI := extractNumber(migrationFiles[i].Name())
		numJ := extractNumber(migrationFiles[j].Name())
		return numI < numJ
	})

	// Execute each migration
	for _, file := range migrationFiles {
		migrationSQL, err := migrationsFS.ReadFile(filepath.Join("migrations", file.Name()))
		if err != nil {
			return fmt.Errorf("failed to read migration file %s: %w", file.Name(), err)
		}

		if _, err := DB.Exec(string(migrationSQL)); err != nil {
			return fmt.Errorf("failed to execute migration %s: %w", file.Name(), err)
		}

		fmt.Printf("✓ Executed migration: %s\n", file.Name())
	}

	return nil
}

// extractNumber extracts the numeric prefix from a filename
func extractNumber(filename string) int {
	parts := strings.Split(filename, "_")
	if len(parts) > 0 {
		if num, err := strconv.Atoi(parts[0]); err == nil {
			return num
		}
	}
	return 0
}

