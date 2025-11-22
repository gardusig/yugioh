package com.yugioh.controller;

import com.yugioh.dto.DeckSummary;
import com.yugioh.dto.DeckWithCards;
import com.yugioh.dto.PaginationResponse;
import com.yugioh.service.DeckService;
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
@DisplayName("DeckController Tests")
class DeckControllerTest {

    @Mock
    private DeckService deckService;

    @InjectMocks
    private DeckController deckController;

    private DeckSummary testDeck1;
    private DeckSummary testDeck2;
    private List<DeckSummary> testDecks;

    @BeforeEach
    void setUp() {
        testDeck1 = new DeckSummary(1, "Yugi's Deck", "Yugi's main deck", "Yugi Muto",
                                "Dark Magician", "Dark", 100, 95, 40, true);
        testDeck2 = new DeckSummary(2, "Kaiba's Deck", "Kaiba's main deck", "Seto Kaiba",
                                "Blue-Eyes", "Light", 100, 98, 40, true);
        testDecks = Arrays.asList(testDeck1, testDeck2);
    }

    @Test
    @DisplayName("Should get all decks with page parameter")
    void getAllDecks_WithPage_ReturnsPaginatedDecks() {
        // Given
        int page = 1;
        int limit = 20;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.getAllDecks(eq(page), eq(limit), isNull(), isNull())).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(page, limit, null, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().get("decks")).isEqualTo(testDecks);

        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination).isNotNull();
        assertThat(pagination.getPage()).isEqualTo(1);
        assertThat(pagination.getLimit()).isEqualTo(20);
        assertThat(pagination.getTotal()).isEqualTo(50L);
    }

    @Test
    @DisplayName("Should get all decks with firstDeck parameter")
    void getAllDecks_WithFirstDeck_CalculatesCorrectPage() {
        // Given
        int limit = 20;
        Integer firstDeck = 5;
        int calculatedPage = 1;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.calculatePageFromDeckId(eq(firstDeck), eq(limit), isNull(), eq(false)))
            .thenReturn(calculatedPage);
        when(deckService.getAllDecks(eq(calculatedPage), eq(limit), isNull(), isNull()))
            .thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(null, limit, firstDeck, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().get("decks")).isEqualTo(testDecks);
    }

    @Test
    @DisplayName("Should default to page 1 when no parameters provided")
    void getAllDecks_NoParameters_DefaultsToPageOne() {
        // Given
        int limit = 20;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.getAllDecks(eq(1), eq(limit), isNull(), isNull())).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(null, limit, null, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should prioritize firstDeck over page parameter")
    void getAllDecks_FirstDeckTakesPrecedence_OverPage() {
        // Given
        int page = 5;
        int limit = 20;
        Integer firstDeck = 10;
        int calculatedPage = 1;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.calculatePageFromDeckId(eq(firstDeck), eq(limit), isNull(), eq(false)))
            .thenReturn(calculatedPage);
        when(deckService.getAllDecks(eq(calculatedPage), eq(limit), isNull(), isNull()))
            .thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(page, limit, firstDeck, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(calculatedPage);
    }

    @Test
    @DisplayName("Should filter decks by archetype")
    void getAllDecks_WithArchetype_ReturnsFilteredDecks() {
        // Given
        int page = 1;
        int limit = 20;
        String archetype = "Dark Magician";
        Page<DeckSummary> deckPage = new PageImpl<>(Arrays.asList(testDeck1), PageRequest.of(0, limit), 10);

        when(deckService.getAllDecks(eq(page), eq(limit), eq(archetype), isNull())).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(page, limit, null, archetype, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        @SuppressWarnings("unchecked")
        List<DeckSummary> decks = (List<DeckSummary>) response.getBody().get("decks");
        assertThat(decks).hasSize(1);
        assertThat(decks.get(0).getArchetype()).isEqualTo(archetype);
    }

    @Test
    @DisplayName("Should filter preset decks only")
    void getAllDecks_WithPresetFilter_ReturnsPresetDecks() {
        // Given
        int page = 1;
        int limit = 20;
        Boolean preset = true;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 30);

        when(deckService.getAllDecks(eq(page), eq(limit), isNull(), eq(true))).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(page, limit, null, null, preset);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        @SuppressWarnings("unchecked")
        List<DeckSummary> decks = (List<DeckSummary>) response.getBody().get("decks");
        assertThat(decks).allMatch(DeckSummary::getIsPreset);
    }

    @Test
    @DisplayName("Should get deck by ID when deck exists")
    void getDeckById_WhenDeckExists_ReturnsDeck() {
        // Given
        Integer deckId = 1;
        DeckWithCards deckWithCards = new DeckWithCards();
        deckWithCards.setId(deckId);
        deckWithCards.setName("Yugi's Deck");

        when(deckService.getDeckById(deckId)).thenReturn(Optional.of(deckWithCards));

        // When
        ResponseEntity<DeckWithCards> response = deckController.getDeckById(deckId);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getId()).isEqualTo(deckId);
        assertThat(response.getBody().getName()).isEqualTo("Yugi's Deck");
    }

    @Test
    @DisplayName("Should return 404 when deck does not exist")
    void getDeckById_WhenDeckNotExists_ReturnsNotFound() {
        // Given
        Integer deckId = 999;
        when(deckService.getDeckById(deckId)).thenReturn(Optional.empty());

        // When
        ResponseEntity<DeckWithCards> response = deckController.getDeckById(deckId);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).isNull();
    }

    @Test
    @DisplayName("Should handle invalid firstDeck (zero or negative)")
    void getAllDecks_WithInvalidFirstDeck_DefaultsToPageOne() {
        // Given
        int limit = 20;
        Integer invalidFirstDeck = 0;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.getAllDecks(eq(1), eq(limit), isNull(), isNull())).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(null, limit, invalidFirstDeck, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should handle invalid page (zero or negative)")
    void getAllDecks_WithInvalidPage_DefaultsToPageOne() {
        // Given
        int invalidPage = 0;
        int limit = 20;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(0, limit), 50);

        when(deckService.getAllDecks(eq(1), eq(limit), isNull(), isNull())).thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(invalidPage, limit, null, null, null);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(1);
    }

    @Test
    @DisplayName("Should handle preset filter with firstDeck")
    void getAllDecks_WithFirstDeckAndPreset_CalculatesCorrectPage() {
        // Given
        int limit = 20;
        Integer firstDeck = 5;
        Boolean preset = true;
        int calculatedPage = 2;
        Page<DeckSummary> deckPage = new PageImpl<>(testDecks, PageRequest.of(1, limit), 50);

        when(deckService.calculatePageFromDeckId(eq(firstDeck), eq(limit), isNull(), eq(true)))
            .thenReturn(calculatedPage);
        when(deckService.getAllDecks(eq(calculatedPage), eq(limit), isNull(), eq(true)))
            .thenReturn(deckPage);

        // When
        ResponseEntity<Map<String, Object>> response = deckController.getAllDecks(null, limit, firstDeck, null, preset);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        PaginationResponse pagination = (PaginationResponse) response.getBody().get("pagination");
        assertThat(pagination.getPage()).isEqualTo(calculatedPage);
    }
}
