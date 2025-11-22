package com.yugioh.model;

import java.io.Serializable;
import java.util.Objects;

public class DeckCardId implements Serializable {
    private Integer deckId;
    private Integer cardId;
    private Integer position;

    public DeckCardId() {}

    public DeckCardId(Integer deckId, Integer cardId, Integer position) {
        this.deckId = deckId;
        this.cardId = cardId;
        this.position = position;
    }

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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DeckCardId that = (DeckCardId) o;
        return Objects.equals(deckId, that.deckId) &&
            Objects.equals(cardId, that.cardId) &&
            Objects.equals(position, that.position);
    }

    @Override
    public int hashCode() {
        return Objects.hash(deckId, cardId, position);
    }
}
