package com.yugioh.model;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("DeckCardId Tests")
class DeckCardIdTest {

    @Test
    @DisplayName("Should create DeckCardId with no-args constructor")
    void constructor_NoArgs_CreatesEmptyObject() {
        // When
        DeckCardId deckCardId = new DeckCardId();

        // Then
        assertThat(deckCardId).isNotNull();
        assertThat(deckCardId.getDeckId()).isNull();
        assertThat(deckCardId.getCardId()).isNull();
        assertThat(deckCardId.getPosition()).isNull();
    }

    @Test
    @DisplayName("Should create DeckCardId with all parameters")
    void constructor_WithAllParams_SetsAllFields() {
        // Given
        Integer deckId = 1;
        Integer cardId = 2;
        Integer position = 3;

        // When
        DeckCardId deckCardId = new DeckCardId(deckId, cardId, position);

        // Then
        assertThat(deckCardId.getDeckId()).isEqualTo(deckId);
        assertThat(deckCardId.getCardId()).isEqualTo(cardId);
        assertThat(deckCardId.getPosition()).isEqualTo(position);
    }

    @Test
    @DisplayName("Should set and get all fields")
    void setters_AndGetters_WorkCorrectly() {
        // Given
        DeckCardId deckCardId = new DeckCardId();
        Integer deckId = 5;
        Integer cardId = 10;
        Integer position = 15;

        // When
        deckCardId.setDeckId(deckId);
        deckCardId.setCardId(cardId);
        deckCardId.setPosition(position);

        // Then
        assertThat(deckCardId.getDeckId()).isEqualTo(deckId);
        assertThat(deckCardId.getCardId()).isEqualTo(cardId);
        assertThat(deckCardId.getPosition()).isEqualTo(position);
    }

    @Test
    @DisplayName("Should return true for equal objects")
    void equals_WithEqualObjects_ReturnsTrue() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);
        DeckCardId id2 = new DeckCardId(1, 2, 3);

        // When/Then
        assertThat(id1.equals(id2)).isTrue();
        assertThat(id1).isEqualTo(id2);
    }

    @Test
    @DisplayName("Should return false for different objects")
    void equals_WithDifferentObjects_ReturnsFalse() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);
        DeckCardId id2 = new DeckCardId(1, 2, 4);
        DeckCardId id3 = new DeckCardId(1, 3, 3);
        DeckCardId id4 = new DeckCardId(2, 2, 3);

        // When/Then
        assertThat(id1.equals(id2)).isFalse();
        assertThat(id1.equals(id3)).isFalse();
        assertThat(id1.equals(id4)).isFalse();
    }

    @Test
    @DisplayName("Should return false when comparing with null")
    void equals_WithNull_ReturnsFalse() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);

        // When/Then
        assertThat(id1.equals(null)).isFalse();
    }

    @Test
    @DisplayName("Should return false when comparing with different class")
    void equals_WithDifferentClass_ReturnsFalse() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);
        String other = "not a DeckCardId";

        // When/Then
        assertThat(id1.equals(other)).isFalse();
    }

    @Test
    @DisplayName("Should return true when comparing with itself")
    void equals_WithItself_ReturnsTrue() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);

        // When/Then
        assertThat(id1.equals(id1)).isTrue();
    }

    @Test
    @DisplayName("Should return same hashCode for equal objects")
    void hashCode_WithEqualObjects_ReturnsSameHashCode() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);
        DeckCardId id2 = new DeckCardId(1, 2, 3);

        // When/Then
        assertThat(id1.hashCode()).isEqualTo(id2.hashCode());
    }

    @Test
    @DisplayName("Should return different hashCode for different objects")
    void hashCode_WithDifferentObjects_ReturnsDifferentHashCode() {
        // Given
        DeckCardId id1 = new DeckCardId(1, 2, 3);
        DeckCardId id2 = new DeckCardId(1, 2, 4);

        // When/Then
        assertThat(id1.hashCode()).isNotEqualTo(id2.hashCode());
    }

    @Test
    @DisplayName("Should handle null values in equals")
    void equals_WithNullValues_HandlesCorrectly() {
        // Given
        DeckCardId id1 = new DeckCardId(null, 2, 3);
        DeckCardId id2 = new DeckCardId(null, 2, 3);
        DeckCardId id3 = new DeckCardId(1, 2, 3);

        // When/Then
        assertThat(id1.equals(id2)).isTrue();
        assertThat(id1.equals(id3)).isFalse();
    }

    @Test
    @DisplayName("Should handle null values in hashCode")
    void hashCode_WithNullValues_HandlesCorrectly() {
        // Given
        DeckCardId id1 = new DeckCardId(null, 2, 3);
        DeckCardId id2 = new DeckCardId(null, 2, 3);

        // When/Then
        assertThat(id1.hashCode()).isEqualTo(id2.hashCode());
    }
}
