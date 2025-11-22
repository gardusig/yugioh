package com.yugioh.service;

import com.yugioh.dto.DeckSummary;
import com.yugioh.dto.DeckWithCards;
import com.yugioh.model.Card;
import com.yugioh.model.Deck;
import com.yugioh.repository.CardRepository;
import com.yugioh.repository.DeckCardRepository;
import com.yugioh.repository.DeckRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("DeckService Tests")
class DeckServiceTest {

    @Mock
    private DeckRepository deckRepository;

    @Mock
    private DeckCardRepository deckCardRepository;

    @Mock
    private CardRepository cardRepository;

    @InjectMocks
    private DeckService deckService;

    private Deck testDeck1;
    private Deck testDeck2;
    private Card testCard1;
    private Card testCard2;
    private Card testCard3;

    @BeforeEach
    void setUp() {
        testDeck1 = new Deck();
        testDeck1.setId(1);
        testDeck1.setName("Yugi's Deck");
        testDeck1.setDescription("Yugi's main deck");
        testDeck1.setCharacterName("Yugi Muto");
        testDeck1.setArchetype("Dark Magician");
        testDeck1.setMaxCost(100);
        testDeck1.setIsPreset(true);

        testDeck2 = new Deck();
        testDeck2.setId(2);
        testDeck2.setName("Kaiba's Deck");
        testDeck2.setDescription("Kaiba's main deck");
        testDeck2.setCharacterName("Seto Kaiba");
        testDeck2.setArchetype("Blue-Eyes");
        testDeck2.setMaxCost(100);
        testDeck2.setIsPreset(true);

        testCard1 = new Card();
        testCard1.setId(1);
        testCard1.setName("Dark Magician");
        testCard1.setType("Monster");
        testCard1.setAttribute("Dark");
        testCard1.setCost(5);

        testCard2 = new Card();
        testCard2.setId(2);
        testCard2.setName("Dark Magician Girl");
        testCard2.setType("Monster");
        testCard2.setAttribute("Dark");
        testCard2.setCost(4);

        testCard3 = new Card();
        testCard3.setId(3);
        testCard3.setName("Mystical Space Typhoon");
        testCard3.setType("Spell");
        testCard3.setCost(2);
    }

    @Test
    @DisplayName("Should get all decks without filters")
    void getAllDecks_WithoutFilters_ReturnsAllDecks() {
        // Given
        int page = 1;
        int limit = 20;
        PageRequest pageRequest = PageRequest.of(page - 1, limit);
        Page<Deck> deckPage = new PageImpl<>(Arrays.asList(testDeck1, testDeck2), pageRequest, 50);
        List<Integer> cardIds1 = Arrays.asList(1, 2);
        List<Integer> cardIds2 = Arrays.asList(3);

        when(deckRepository.findAllWithFilters(null, null, pageRequest)).thenReturn(deckPage);
        when(deckCardRepository.findCardIdsByDeckId(1)).thenReturn(cardIds1);
        when(deckCardRepository.findCardIdsByDeckId(2)).thenReturn(cardIds2);
        when(cardRepository.findByIds(cardIds1)).thenReturn(Arrays.asList(testCard1, testCard2));
        when(cardRepository.findByIds(cardIds2)).thenReturn(Arrays.asList(testCard3));

        // When
        Page<DeckSummary> result = deckService.getAllDecks(page, limit, null, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(2);
        assertThat(result.getTotalElements()).isEqualTo(50L);

        DeckSummary summary1 = result.getContent().get(0);
        assertThat(summary1.getId()).isEqualTo(1);
        assertThat(summary1.getName()).isEqualTo("Yugi's Deck");
        assertThat(summary1.getCardCount()).isEqualTo(2);
        assertThat(summary1.getTotalCost()).isEqualTo(9); // 5 + 4
        assertThat(summary1.getMostCommonType()).isEqualTo("Dark");

        verify(deckRepository).findAllWithFilters(null, null, pageRequest);
    }

    @Test
    @DisplayName("Should get all decks with archetype filter")
    void getAllDecks_WithArchetype_ReturnsFilteredDecks() {
        // Given
        int page = 1;
        int limit = 20;
        String archetype = "Dark Magician";
        PageRequest pageRequest = PageRequest.of(page - 1, limit);
        Page<Deck> deckPage = new PageImpl<>(Arrays.asList(testDeck1), pageRequest, 10);
        List<Integer> cardIds = Arrays.asList(1, 2);

        when(deckRepository.findAllWithFilters(archetype, null, pageRequest)).thenReturn(deckPage);
        when(deckCardRepository.findCardIdsByDeckId(1)).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(Arrays.asList(testCard1, testCard2));

        // When
        Page<DeckSummary> result = deckService.getAllDecks(page, limit, archetype, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).getArchetype()).isEqualTo(archetype);
        verify(deckRepository).findAllWithFilters(archetype, null, pageRequest);
    }

    @Test
    @DisplayName("Should get all decks with preset filter")
    void getAllDecks_WithPresetFilter_ReturnsPresetDecks() {
        // Given
        int page = 1;
        int limit = 20;
        Boolean presetOnly = true;
        PageRequest pageRequest = PageRequest.of(page - 1, limit);
        Page<Deck> deckPage = new PageImpl<>(Arrays.asList(testDeck1, testDeck2), pageRequest, 30);
        List<Integer> cardIds = Arrays.asList(1);

        when(deckRepository.findAllWithFilters(null, presetOnly, pageRequest)).thenReturn(deckPage);
        when(deckCardRepository.findCardIdsByDeckId(anyInt())).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(Arrays.asList(testCard1));

        // When
        Page<DeckSummary> result = deckService.getAllDecks(page, limit, null, presetOnly);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).allMatch(DeckSummary::getIsPreset);
        verify(deckRepository).findAllWithFilters(null, presetOnly, pageRequest);
    }

    @Test
    @DisplayName("Should get deck by ID when deck exists")
    void getDeckById_WhenDeckExists_ReturnsDeckWithCards() {
        // Given
        Integer deckId = 1;
        List<Integer> cardIds = Arrays.asList(1, 2);
        List<Card> cards = Arrays.asList(testCard1, testCard2);

        when(deckRepository.findById(deckId)).thenReturn(Optional.of(testDeck1));
        when(deckCardRepository.findCardIdsByDeckId(deckId)).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(cards);

        // When
        Optional<DeckWithCards> result = deckService.getDeckById(deckId);

        // Then
        assertThat(result).isPresent();
        DeckWithCards deckWithCards = result.get();
        assertThat(deckWithCards.getId()).isEqualTo(deckId);
        assertThat(deckWithCards.getName()).isEqualTo("Yugi's Deck");
        assertThat(deckWithCards.getCards()).hasSize(2);
        assertThat(deckWithCards.getTotalCost()).isEqualTo(9); // 5 + 4
        assertThat(deckWithCards.getMostCommonType()).isEqualTo("Dark");
        verify(deckRepository).findById(deckId);
        verify(deckCardRepository).findCardIdsByDeckId(deckId);
        verify(cardRepository).findByIds(cardIds);
    }

    @Test
    @DisplayName("Should return empty when deck does not exist")
    void getDeckById_WhenDeckNotExists_ReturnsEmpty() {
        // Given
        Integer deckId = 999;
        when(deckRepository.findById(deckId)).thenReturn(Optional.empty());

        // When
        Optional<DeckWithCards> result = deckService.getDeckById(deckId);

        // Then
        assertThat(result).isEmpty();
        verify(deckRepository).findById(deckId);
    }

    @Test
    @DisplayName("Should calculate most common type correctly for monsters")
    void calculateMostCommonType_WithMonsters_ReturnsMostCommonAttribute() {
        // Given
        Integer deckId = 1;
        List<Integer> cardIds = Arrays.asList(1, 2);
        List<Card> cards = Arrays.asList(testCard1, testCard2); // Both Dark attribute

        when(deckRepository.findById(deckId)).thenReturn(Optional.of(testDeck1));
        when(deckCardRepository.findCardIdsByDeckId(deckId)).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(cards);

        // When
        Optional<DeckWithCards> result = deckService.getDeckById(deckId);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getMostCommonType()).isEqualTo("Dark");
    }

    @Test
    @DisplayName("Should calculate most common type for spells/traps")
    void calculateMostCommonType_WithSpells_ReturnsSpellType() {
        // Given
        Integer deckId = 1;
        List<Integer> cardIds = Arrays.asList(3);
        List<Card> cards = Arrays.asList(testCard3); // Spell type

        when(deckRepository.findById(deckId)).thenReturn(Optional.of(testDeck1));
        when(deckCardRepository.findCardIdsByDeckId(deckId)).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(cards);

        // When
        Optional<DeckWithCards> result = deckService.getDeckById(deckId);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getMostCommonType()).isEqualTo("Spell");
    }

    @Test
    @DisplayName("Should return null for most common type when no cards")
    void calculateMostCommonType_WithNoCards_ReturnsNull() {
        // Given
        Integer deckId = 1;
        List<Integer> cardIds = List.of();
        List<Card> cards = List.of();

        when(deckRepository.findById(deckId)).thenReturn(Optional.of(testDeck1));
        when(deckCardRepository.findCardIdsByDeckId(deckId)).thenReturn(cardIds);
        when(cardRepository.findByIds(cardIds)).thenReturn(cards);

        // When
        Optional<DeckWithCards> result = deckService.getDeckById(deckId);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getMostCommonType()).isNull();
    }

    @Test
    @DisplayName("Should calculate page from deck ID correctly")
    void calculatePageFromDeckId_ReturnsCorrectPage() {
        // Given
        int deckId = 5;
        int limit = 20;
        String archetype = null;
        boolean presetOnly = false;
        long countBefore = 25L;

        when(deckRepository.countDecksBeforeId(deckId, archetype, presetOnly)).thenReturn(countBefore);

        // When
        int result = deckService.calculatePageFromDeckId(deckId, limit, archetype, presetOnly);

        // Then
        // 25 decks before, 20 per page = page 2 (1-based)
        assertThat(result).isEqualTo(2);
        verify(deckRepository).countDecksBeforeId(deckId, archetype, presetOnly);
    }

    @Test
    @DisplayName("Should calculate page from deck ID with filters")
    void calculatePageFromDeckId_WithFilters_ReturnsCorrectPage() {
        // Given
        int deckId = 10;
        int limit = 20;
        String archetype = "Dark Magician";
        boolean presetOnly = true;
        long countBefore = 5L;

        when(deckRepository.countDecksBeforeId(deckId, archetype, presetOnly)).thenReturn(countBefore);

        // When
        int result = deckService.calculatePageFromDeckId(deckId, limit, archetype, presetOnly);

        // Then
        // 5 decks before, 20 per page = page 1 (1-based)
        assertThat(result).isEqualTo(1);
        verify(deckRepository).countDecksBeforeId(deckId, archetype, presetOnly);
    }

    @Test
    @DisplayName("Should handle empty deck cards list")
    void getAllDecks_WithEmptyCards_ReturnsZeroCost() {
        // Given
        int page = 1;
        int limit = 20;
        PageRequest pageRequest = PageRequest.of(page - 1, limit);
        Page<Deck> deckPage = new PageImpl<>(Arrays.asList(testDeck1), pageRequest, 10);
        List<Integer> emptyCardIds = List.of();

        when(deckRepository.findAllWithFilters(null, null, pageRequest)).thenReturn(deckPage);
        when(deckCardRepository.findCardIdsByDeckId(1)).thenReturn(emptyCardIds);
        when(cardRepository.findByIds(emptyCardIds)).thenReturn(List.of());

        // When
        Page<DeckSummary> result = deckService.getAllDecks(page, limit, null, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        DeckSummary summary = result.getContent().get(0);
        assertThat(summary.getCardCount()).isEqualTo(0);
        assertThat(summary.getTotalCost()).isEqualTo(0);
        assertThat(summary.getMostCommonType()).isNull();
    }
}
