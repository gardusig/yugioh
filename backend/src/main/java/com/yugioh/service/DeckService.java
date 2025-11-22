package com.yugioh.service;

import com.yugioh.dto.DeckSummary;
import com.yugioh.dto.DeckWithCards;
import com.yugioh.model.Card;
import com.yugioh.model.Deck;
import com.yugioh.repository.CardRepository;
import com.yugioh.repository.DeckCardRepository;
import com.yugioh.repository.DeckRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.function.Function;

@Service
public class DeckService {
    @Autowired
    private DeckRepository deckRepository;

    @Autowired
    private DeckCardRepository deckCardRepository;

    @Autowired
    private CardRepository cardRepository;

    public Page<DeckSummary> getAllDecks(int page, int limit, String archetype, Boolean presetOnly) {
        Pageable pageable = PageRequest.of(page - 1, limit);
        Page<Deck> decks = deckRepository.findAllWithFilters(archetype, presetOnly, pageable);

        return decks.map(deck -> {
            List<Integer> cardIds = deckCardRepository.findCardIdsByDeckId(deck.getId());
            List<Card> cards = cardRepository.findByIds(cardIds);
            int totalCost = cards.stream().mapToInt(Card::getCost).sum();
            String mostCommonType = calculateMostCommonType(cards);

            return new DeckSummary(
                deck.getId(),
                deck.getName(),
                deck.getDescription(),
                deck.getCharacterName(),
                deck.getArchetype(),
                mostCommonType,
                deck.getMaxCost(),
                totalCost,
                cardIds.size(),
                deck.getIsPreset()
            );
        });
    }

    public int calculatePageFromDeckId(int deckId, int limit, String archetype, Boolean presetOnly) {
        // Count how many decks come before this deck ID with the same filters
        long countBefore = deckRepository.countDecksBeforeId(deckId, archetype, presetOnly);
        // Calculate which page this deck would be on (1-based)
        return (int) ((countBefore / limit) + 1);
    }

    public Optional<DeckWithCards> getDeckById(Integer id) {
        Optional<Deck> deckOpt = deckRepository.findById(id);
        if (deckOpt.isEmpty()) {
            return Optional.empty();
        }

        Deck deck = deckOpt.get();
        List<Integer> cardIds = deckCardRepository.findCardIdsByDeckId(id);
        List<Card> cards = cardRepository.findByIds(cardIds);
        int totalCost = cards.stream().mapToInt(Card::getCost).sum();
        String mostCommonType = calculateMostCommonType(cards);

        DeckWithCards deckWithCards = new DeckWithCards();
        deckWithCards.setId(deck.getId());
        deckWithCards.setName(deck.getName());
        deckWithCards.setDescription(deck.getDescription());
        deckWithCards.setCharacterName(deck.getCharacterName());
        deckWithCards.setArchetype(deck.getArchetype());
        deckWithCards.setMostCommonType(mostCommonType);
        deckWithCards.setCards(cards);
        deckWithCards.setMaxCost(deck.getMaxCost());
        deckWithCards.setTotalCost(totalCost);
        deckWithCards.setIsPreset(deck.getIsPreset());

        return Optional.of(deckWithCards);
    }

    /**
     * Calculate the most common type/attribute in a deck.
     * For monsters, uses attribute (Dark, Light, Water, etc.)
     * For spells/traps, uses type (Spell, Trap)
     * Returns the most frequently occurring type/attribute.
     */
    private String calculateMostCommonType(List<Card> cards) {
        if (cards == null || cards.isEmpty()) {
            return null;
        }

        // Count occurrences of each type/attribute
        Map<String, Long> typeCounts = cards.stream()
            .filter(card -> card.getType() != null)
            .map(card -> {
                // For monsters, use attribute; for spells/traps, use type
                if ("Monster".equalsIgnoreCase(card.getType()) && card.getAttribute() != null) {
                    return card.getAttribute();
                }
                return card.getType();
            })
            .filter(type -> type != null && !type.isEmpty())
            .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

        if (typeCounts.isEmpty()) {
            return null;
        }

        // Find the most common type
        return typeCounts.entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .map(Map.Entry::getKey)
            .orElse(null);
    }
}
