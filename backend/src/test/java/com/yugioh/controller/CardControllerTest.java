package com.yugioh.controller;

import com.yugioh.dto.PaginationResponse;
import com.yugioh.model.Card;
import com.yugioh.service.CardService;
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
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("CardController Tests")
class CardControllerTest {

    @Mock
    private CardService cardService;

    @InjectMocks
    private CardController cardController;

    private Card testCard1;
    private Card testCard2;
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

        testCards = Arrays.asList(testCard1, testCard2);
    }

    @Test
    @DisplayName("Should get all cards with page parameter")
    void getAllCards_WithPage_ReturnsPaginatedCards() {
        // Given
        int page = 1;
        int limit = 24;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 100);

        when(cardService.getAllCards(eq(page), eq(limit), isNull())).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(page, limit, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().get("cards")).isEqualTo(testCards);

        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination).isNotNull();
        assertThat(pagination.getPage()).isEqualTo(1);
        assertThat(pagination.getLimit()).isEqualTo(24);
        assertThat(pagination.getTotal()).isEqualTo(100L);
    }

    @Test
    @DisplayName("Should get all cards with firstCard parameter")
    void getAllCards_WithFirstCard_ReturnsFilteredCards() {
        // Given
        int limit = 24;
        Integer firstCard = 25;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 50);

        when(cardService.getAllCards(eq(1), eq(limit), eq(firstCard))).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(null, limit, firstCard);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().get("cards")).isEqualTo(testCards);

        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination).isNotNull();
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should default to page 1 when no parameters provided")
    void getAllCards_NoParameters_DefaultsToPageOne() {
        // Given
        int limit = 24;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 100);

        when(cardService.getAllCards(eq(1), eq(limit), isNull())).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(null, limit, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();

        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should prioritize firstCard over page parameter")
    void getAllCards_FirstCardTakesPrecedence_OverPage() {
        // Given
        int page = 5;
        int limit = 24;
        Integer firstCard = 50;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 50);

        when(cardService.getAllCards(eq(1), eq(limit), eq(firstCard))).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(page, limit, firstCard);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should get card by ID when card exists")
    void getCardById_WhenCardExists_ReturnsCard() {
        // Given
        Integer cardId = 1;
        when(cardService.getCardById(cardId)).thenReturn(Optional.of(testCard1));

        // When
        ResponseEntity<Card> response = cardController.getCardById(cardId);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getId()).isEqualTo(cardId);
        assertThat(response.getBody().getName()).isEqualTo("Blue-Eyes White Dragon");
    }

    @Test
    @DisplayName("Should return 404 when card does not exist")
    void getCardById_WhenCardNotExists_ReturnsNotFound() {
        // Given
        Integer cardId = 999;
        when(cardService.getCardById(cardId)).thenReturn(Optional.empty());

        // When
        ResponseEntity<Card> response = cardController.getCardById(cardId);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).isNull();
    }

    @Test
    @DisplayName("Should handle invalid firstCard (zero or negative)")
    void getAllCards_WithInvalidFirstCard_DefaultsToPageOne() {
        // Given
        int limit = 24;
        Integer invalidFirstCard = 0;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 100);

        when(cardService.getAllCards(eq(1), eq(limit), isNull())).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(null, limit, invalidFirstCard);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should handle invalid page (zero or negative)")
    void getAllCards_WithInvalidPage_DefaultsToPageOne() {
        // Given
        int invalidPage = 0;
        int limit = 24;
        Page<Card> cardPage = new PageImpl<>(testCards, PageRequest.of(0, limit), 100);

        when(cardService.getAllCards(eq(1), eq(limit), isNull())).thenReturn(cardPage);

        // When
        ResponseEntity<Map<String, Object>> response = cardController.getAllCards(invalidPage, limit, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }
}
