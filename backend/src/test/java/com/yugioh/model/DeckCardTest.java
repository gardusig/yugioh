package com.yugioh.model;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("DeckCard Model Tests")
class DeckCardTest {

    private DeckCard deckCard;

    @BeforeEach
    void setUp() {
        deckCard = new DeckCard();
    }

    @Test
    @DisplayName("Should set and get deck id")
    void setDeckId_And_GetDeckId() {
        Integer deckId = 1;
        deckCard.setDeckId(deckId);
        assertThat(deckCard.getDeckId()).isEqualTo(deckId);
    }

    @Test
    @DisplayName("Should set and get card id")
    void setCardId_And_GetCardId() {
        Integer cardId = 1;
        deckCard.setCardId(cardId);
        assertThat(deckCard.getCardId()).isEqualTo(cardId);
    }

    @Test
    @DisplayName("Should set and get position")
    void setPosition_And_GetPosition() {
        Integer position = 1;
        deckCard.setPosition(position);
        assertThat(deckCard.getPosition()).isEqualTo(position);
    }
}
