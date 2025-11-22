package com.yugioh.model;

import jakarta.persistence.*;

@Entity
@Table(name = "deck_cards")
@IdClass(DeckCardId.class)
public class DeckCard {
    @Id
    @Column(name = "deck_id")
    private Integer deckId;

    @Id
    @Column(name = "card_id")
    private Integer cardId;

    @Id
    @Column(name = "position")
    private Integer position;

    // Getters and Setters
    public Integer getDeckId() {
        return deckId;
    }

    public void setDeckId(Integer deckId) {
        this.deckId = deckId;
    }

    public Integer getCardId() {
        return cardId;
    }

    public void setCardId(Integer cardId) {
        this.cardId = cardId;
    }

    public Integer getPosition() {
        return position;
    }

    public void setPosition(Integer position) {
        this.position = position;
    }
}
