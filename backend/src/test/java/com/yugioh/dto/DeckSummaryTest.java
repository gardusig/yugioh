package com.yugioh.dto;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("DeckSummary Tests")
class DeckSummaryTest {

    @Test
    @DisplayName("Should create DeckSummary with no-args constructor")
    void constructor_NoArgs_CreatesEmptyObject() {
        // When
        DeckSummary summary = new DeckSummary();

        // Then
        assertThat(summary).isNotNull();
        assertThat(summary.getId()).isNull();
        assertThat(summary.getName()).isNull();
        assertThat(summary.getDescription()).isNull();
        assertThat(summary.getCharacterName()).isNull();
        assertThat(summary.getArchetype()).isNull();
        assertThat(summary.getMostCommonType()).isNull();
        assertThat(summary.getMaxCost()).isNull();
        assertThat(summary.getTotalCost()).isNull();
        assertThat(summary.getCardCount()).isNull();
        assertThat(summary.getIsPreset()).isNull();
    }

    @Test
    @DisplayName("Should create DeckSummary with all parameters")
    void constructor_WithAllParams_SetsAllFields() {
        // Given
        Integer id = 1;
        String name = "Test Deck";
        String description = "Test Description";
        String characterName = "Test Character";
        String archetype = "Test Archetype";
        String mostCommonType = "Dark";
        Integer maxCost = 100;
        Integer totalCost = 95;
        Integer cardCount = 40;
        Boolean isPreset = true;

        // When
        DeckSummary summary = new DeckSummary(id, name, description, characterName,
                                            archetype, mostCommonType, maxCost, totalCost,
                                            cardCount, isPreset);

        // Then
        assertThat(summary.getId()).isEqualTo(id);
        assertThat(summary.getName()).isEqualTo(name);
        assertThat(summary.getDescription()).isEqualTo(description);
        assertThat(summary.getCharacterName()).isEqualTo(characterName);
        assertThat(summary.getArchetype()).isEqualTo(archetype);
        assertThat(summary.getMostCommonType()).isEqualTo(mostCommonType);
        assertThat(summary.getMaxCost()).isEqualTo(maxCost);
        assertThat(summary.getTotalCost()).isEqualTo(totalCost);
        assertThat(summary.getCardCount()).isEqualTo(cardCount);
        assertThat(summary.getIsPreset()).isEqualTo(isPreset);
    }

    @Test
    @DisplayName("Should set and get all fields")
    void setters_AndGetters_WorkCorrectly() {
        // Given
        DeckSummary summary = new DeckSummary();
        Integer id = 2;
        String name = "Another Deck";
        String description = "Another Description";
        String characterName = "Another Character";
        String archetype = "Another Archetype";
        String mostCommonType = "Light";
        Integer maxCost = 150;
        Integer totalCost = 120;
        Integer cardCount = 35;
        Boolean isPreset = false;

        // When
        summary.setId(id);
        summary.setName(name);
        summary.setDescription(description);
        summary.setCharacterName(characterName);
        summary.setArchetype(archetype);
        summary.setMostCommonType(mostCommonType);
        summary.setMaxCost(maxCost);
        summary.setTotalCost(totalCost);
        summary.setCardCount(cardCount);
        summary.setIsPreset(isPreset);

        // Then
        assertThat(summary.getId()).isEqualTo(id);
        assertThat(summary.getName()).isEqualTo(name);
        assertThat(summary.getDescription()).isEqualTo(description);
        assertThat(summary.getCharacterName()).isEqualTo(characterName);
        assertThat(summary.getArchetype()).isEqualTo(archetype);
        assertThat(summary.getMostCommonType()).isEqualTo(mostCommonType);
        assertThat(summary.getMaxCost()).isEqualTo(maxCost);
        assertThat(summary.getTotalCost()).isEqualTo(totalCost);
        assertThat(summary.getCardCount()).isEqualTo(cardCount);
        assertThat(summary.getIsPreset()).isEqualTo(isPreset);
    }
}
