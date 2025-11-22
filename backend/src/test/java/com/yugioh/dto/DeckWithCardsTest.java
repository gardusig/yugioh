package com.yugioh.dto;

import com.yugioh.model.Card;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("DeckWithCards Tests")
class DeckWithCardsTest {

    @Test
    @DisplayName("Should create DeckWithCards with no-args constructor")
    void constructor_NoArgs_CreatesEmptyObject() {
        // When
        DeckWithCards deckWithCards = new DeckWithCards();

        // Then
        assertThat(deckWithCards).isNotNull();
        assertThat(deckWithCards.getId()).isNull();
        assertThat(deckWithCards.getName()).isNull();
        assertThat(deckWithCards.getDescription()).isNull();
        assertThat(deckWithCards.getCharacterName()).isNull();
        assertThat(deckWithCards.getArchetype()).isNull();
        assertThat(deckWithCards.getMostCommonType()).isNull();
        assertThat(deckWithCards.getCards()).isNull();
        assertThat(deckWithCards.getMaxCost()).isNull();
        assertThat(deckWithCards.getTotalCost()).isNull();
        assertThat(deckWithCards.getIsPreset()).isNull();
    }

    @Test
    @DisplayName("Should set and get all fields")
    void setters_AndGetters_WorkCorrectly() {
        // Given
        DeckWithCards deckWithCards = new DeckWithCards();
        Integer id = 1;
        String name = "Test Deck";
        String description = "Test Description";
        String characterName = "Test Character";
        String archetype = "Test Archetype";
        String mostCommonType = "Dark";
        List<Card> cards = Arrays.asList(createTestCard(1), createTestCard(2));
        Integer maxCost = 100;
        Integer totalCost = 95;
        Boolean isPreset = true;

        // When
        deckWithCards.setId(id);
        deckWithCards.setName(name);
        deckWithCards.setDescription(description);
        deckWithCards.setCharacterName(characterName);
        deckWithCards.setArchetype(archetype);
        deckWithCards.setMostCommonType(mostCommonType);
        deckWithCards.setCards(cards);
        deckWithCards.setMaxCost(maxCost);
        deckWithCards.setTotalCost(totalCost);
        deckWithCards.setIsPreset(isPreset);

        // Then
        assertThat(deckWithCards.getId()).isEqualTo(id);
        assertThat(deckWithCards.getName()).isEqualTo(name);
        assertThat(deckWithCards.getDescription()).isEqualTo(description);
        assertThat(deckWithCards.getCharacterName()).isEqualTo(characterName);
        assertThat(deckWithCards.getArchetype()).isEqualTo(archetype);
        assertThat(deckWithCards.getMostCommonType()).isEqualTo(mostCommonType);
        assertThat(deckWithCards.getCards()).isEqualTo(cards);
        assertThat(deckWithCards.getMaxCost()).isEqualTo(maxCost);
        assertThat(deckWithCards.getTotalCost()).isEqualTo(totalCost);
        assertThat(deckWithCards.getIsPreset()).isEqualTo(isPreset);
    }

    @Test
    @DisplayName("Should handle null cards list")
    void setCards_WithNull_WorksCorrectly() {
        // Given
        DeckWithCards deckWithCards = new DeckWithCards();

        // When
        deckWithCards.setCards(null);

        // Then
        assertThat(deckWithCards.getCards()).isNull();
    }

    @Test
    @DisplayName("Should handle empty cards list")
    void setCards_WithEmptyList_WorksCorrectly() {
        // Given
        DeckWithCards deckWithCards = new DeckWithCards();
        List<Card> emptyCards = List.of();

        // When
        deckWithCards.setCards(emptyCards);

        // Then
        assertThat(deckWithCards.getCards()).isEmpty();
    }

    private Card createTestCard(Integer id) {
        Card card = new Card();
        card.setId(id);
        card.setName("Test Card " + id);
        return card;
    }
}
