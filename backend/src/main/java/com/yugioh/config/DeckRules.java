package com.yugioh.config;

/**
 * Deck construction rules: max size and max copies per card.
 */
public final class DeckRules {
    /** Maximum number of cards in a deck. */
    public static final int MAX_DECK_SIZE = 40;

    /** Maximum number of copies of the same card allowed per deck. */
    public static final int MAX_COPIES_PER_CARD = 3;

    private DeckRules() {}
}
