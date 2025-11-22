package com.yugioh.service;

import com.yugioh.model.Card;
import com.yugioh.repository.CardRepository;
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
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("CardService Tests")
@SuppressWarnings("unchecked")
class CardServiceTest {

    @Mock
    private CardRepository cardRepository;

    @InjectMocks
    private CardService cardService;

    private Card testCard1;
    private Card testCard2;
    private Card testCard3;
    private List<Card> testCards;

    @BeforeEach
    void setUp() {
        testCard1 = new Card();
        testCard1.setId(1);
        testCard1.setName("Blue-Eyes White Dragon");
        testCard1.setType("Monster");
        testCard1.setCost(5);

        testCard2 = new Card();
        testCard2.setId(2);
        testCard2.setName("Dark Magician");
        testCard2.setType("Monster");
        testCard2.setCost(4);

        testCard3 = new Card();
        testCard3.setId(3);
        testCard3.setName("Red-Eyes Black Dragon");
        testCard3.setType("Monster");
        testCard3.setCost(6);

        testCards = Arrays.asList(testCard1, testCard2, testCard3);
    }

    @Test
    @DisplayName("Should get all cards without startId filter")
    void getAllCards_WithoutStartId_ReturnsAllCards() {
        // Given
        int page = 1;
        int limit = 24;
        PageRequest pageRequest = PageRequest.of(page - 1, limit, Sort.by("id").ascending());
        Page<Card> cardPage = new PageImpl<>(testCards, pageRequest, 100);

        when(cardRepository.findAll(any(PageRequest.class))).thenReturn(cardPage);

        // When
        Page<Card> result = cardService.getAllCards(page, limit, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(3);
        assertThat(result.getTotalElements()).isEqualTo(100L);
        assertThat(result.getContent()).containsExactlyElementsOf(testCards);
        verify(cardRepository).findAll(pageRequest);
    }

    @Test
    @DisplayName("Should get cards with startId filter")
    void getAllCards_WithStartId_ReturnsFilteredCards() {
        // Given
        int page = 1;
        int limit = 24;
        Integer startId = 2;
        PageRequest pageRequest = PageRequest.of(page - 1, limit, Sort.by("id").ascending());
        List<Card> filteredCards = Arrays.asList(testCard2, testCard3);
        Page<Card> cardPage = new PageImpl<>(filteredCards, pageRequest, 50);

        when(cardRepository.findAll(any(Specification.class), any(PageRequest.class))).thenReturn(cardPage);

        // When
        Page<Card> result = cardService.getAllCards(page, limit, startId);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(2);
        assertThat(result.getTotalElements()).isEqualTo(50L);
        assertThat(result.getContent()).containsExactlyElementsOf(filteredCards);
        verify(cardRepository).findAll(any(Specification.class), eq(pageRequest));
    }

    @Test
    @DisplayName("Should get card by ID when card exists")
    void getCardById_WhenCardExists_ReturnsCard() {
        // Given
        Integer cardId = 1;
        when(cardRepository.findById(cardId)).thenReturn(Optional.of(testCard1));

        // When
        Optional<Card> result = cardService.getCardById(cardId);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(cardId);
        assertThat(result.get().getName()).isEqualTo("Blue-Eyes White Dragon");
        verify(cardRepository).findById(cardId);
    }

    @Test
    @DisplayName("Should return empty when card does not exist")
    void getCardById_WhenCardNotExists_ReturnsEmpty() {
        // Given
        Integer cardId = 999;
        when(cardRepository.findById(cardId)).thenReturn(Optional.empty());

        // When
        Optional<Card> result = cardService.getCardById(cardId);

        // Then
        assertThat(result).isEmpty();
        verify(cardRepository).findById(cardId);
    }

    @Test
    @DisplayName("Should get cards by IDs")
    void getCardsByIds_ReturnsMatchingCards() {
        // Given
        List<Integer> cardIds = Arrays.asList(1, 2);
        List<Card> expectedCards = Arrays.asList(testCard1, testCard2);

        when(cardRepository.findByIds(cardIds)).thenReturn(expectedCards);

        // When
        List<Card> result = cardService.getCardsByIds(cardIds);

        // Then
        assertThat(result).isNotNull();
        assertThat(result).hasSize(2);
        assertThat(result).containsExactlyElementsOf(expectedCards);
        verify(cardRepository).findByIds(cardIds);
    }

    @Test
    @DisplayName("Should handle empty list of card IDs")
    void getCardsByIds_WithEmptyList_ReturnsEmptyList() {
        // Given
        List<Integer> emptyIds = List.of();
        when(cardRepository.findByIds(emptyIds)).thenReturn(List.of());

        // When
        List<Card> result = cardService.getCardsByIds(emptyIds);

        // Then
        assertThat(result).isNotNull();
        assertThat(result).isEmpty();
        verify(cardRepository).findByIds(emptyIds);
    }

    @Test
    @DisplayName("Should handle pagination with different page numbers")
    void getAllCards_WithDifferentPages_ReturnsCorrectPages() {
        // Given
        int page = 2;
        int limit = 24;
        PageRequest pageRequest = PageRequest.of(page - 1, limit, Sort.by("id").ascending());
        Page<Card> cardPage = new PageImpl<>(testCards, pageRequest, 100);

        when(cardRepository.findAll(any(PageRequest.class))).thenReturn(cardPage);

        // When
        Page<Card> result = cardService.getAllCards(page, limit, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getNumber()).isEqualTo(1); // 0-based page number
        verify(cardRepository).findAll(pageRequest);
    }

    @Test
    @DisplayName("Should handle startId filter with zero or negative value")
    void getAllCards_WithInvalidStartId_ReturnsAllCards() {
        // Given
        int page = 1;
        int limit = 24;
        Integer invalidStartId = 0;
        PageRequest pageRequest = PageRequest.of(page - 1, limit, Sort.by("id").ascending());
        Page<Card> cardPage = new PageImpl<>(testCards, pageRequest, 100);

        // When startId is 0 or negative, it should call findAll without Specification
        when(cardRepository.findAll(any(PageRequest.class))).thenReturn(cardPage);

        // When
        Page<Card> result = cardService.getAllCards(page, limit, invalidStartId);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(3);
        verify(cardRepository).findAll(pageRequest);
    }
}
