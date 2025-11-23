package com.yugioh.model;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("Deck Model Tests")
class DeckTest {

    private Deck deck;

    @BeforeEach
    void setUp() {
        deck = new Deck();
    }

    @Test
    @DisplayName("Should set and get id")
    void setId_And_GetId() {
        Integer id = 1;
        deck.setId(id);
        assertThat(deck.getId()).isEqualTo(id);
    }

    @Test
    @DisplayName("Should set and get name")
    void setName_And_GetName() {
        String name = "Yugi's Deck";
        deck.setName(name);
        assertThat(deck.getName()).isEqualTo(name);
    }

    @Test
    @DisplayName("Should set and get description")
    void setDescription_And_GetDescription() {
        String description = "Yugi's main deck";
        deck.setDescription(description);
        assertThat(deck.getDescription()).isEqualTo(description);
    }

    @Test
    @DisplayName("Should set and get character name")
    void setCharacterName_And_GetCharacterName() {
        String characterName = "Yugi Muto";
        deck.setCharacterName(characterName);
        assertThat(deck.getCharacterName()).isEqualTo(characterName);
    }

    @Test
    @DisplayName("Should set and get archetype")
    void setArchetype_And_GetArchetype() {
        String archetype = "Dark Magician";
        deck.setArchetype(archetype);
        assertThat(deck.getArchetype()).isEqualTo(archetype);
    }

    @Test
    @DisplayName("Should set and get most common type")
    void setMostCommonType_And_GetMostCommonType() {
        String mostCommonType = "Dark";
        deck.setMostCommonType(mostCommonType);
        assertThat(deck.getMostCommonType()).isEqualTo(mostCommonType);
    }

    @Test
    @DisplayName("Should set and get max cost")
    void setMaxCost_And_GetMaxCost() {
        Integer maxCost = 250;
        deck.setMaxCost(maxCost);
        assertThat(deck.getMaxCost()).isEqualTo(maxCost);
    }

    @Test
    @DisplayName("Should set and get is preset")
    void setIsPreset_And_GetIsPreset() {
        Boolean isPreset = true;
        deck.setIsPreset(isPreset);
        assertThat(deck.getIsPreset()).isEqualTo(isPreset);
    }

    @Test
    @DisplayName("Should set and get created at")
    void setCreatedAt_And_GetCreatedAt() {
        LocalDateTime createdAt = LocalDateTime.now();
        deck.setCreatedAt(createdAt);
        assertThat(deck.getCreatedAt()).isEqualTo(createdAt);
    }

    @Test
    @DisplayName("Should set and get updated at")
    void setUpdatedAt_And_GetUpdatedAt() {
        LocalDateTime updatedAt = LocalDateTime.now();
        deck.setUpdatedAt(updatedAt);
        assertThat(deck.getUpdatedAt()).isEqualTo(updatedAt);
    }
}
