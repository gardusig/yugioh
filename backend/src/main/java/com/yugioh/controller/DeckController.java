package com.yugioh.controller;

import com.yugioh.dto.DeckSummary;
import com.yugioh.dto.DeckWithCards;
import com.yugioh.dto.PaginationResponse;
import com.yugioh.service.DeckService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/decks")
@CrossOrigin(origins = "*")
@Tag(name = "Decks", description = "API for browsing character decks and example decks")
public class DeckController {
    @Autowired
    private DeckService deckService;

    @GetMapping
    @Operation(summary = "List all decks", description = "Get a paginated list of all decks. Use either 'page' or 'firstDeck' query parameter.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Successful response",
            content = @Content(schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> getAllDecks(
            @Parameter(description = "Page number (1-based). Ignored if firstDeck is provided.", example = "1")
            @RequestParam(required = false) Integer page,
            @Parameter(description = "Number of decks per page", example = "20")
            @RequestParam(defaultValue = "20") int limit,
            @Parameter(description = "First deck ID to start from. Takes precedence over page.", example = "1")
            @RequestParam(required = false) Integer firstDeck,
            @Parameter(description = "Filter by deck archetype")
            @RequestParam(required = false) String archetype,
            @Parameter(description = "Filter preset decks only")
            @RequestParam(required = false) Boolean preset) {

        // Calculate page from firstDeck if provided, otherwise use page (default to 1)
        int calculatedPage = 1;
        if (firstDeck != null && firstDeck > 0) {
            // Calculate which page this deck would be on
            // We need to find the position of the deck in the filtered results
            calculatedPage = deckService.calculatePageFromDeckId(firstDeck, limit, archetype, preset != null && preset);
        } else if (page != null && page > 0) {
            calculatedPage = page;
        }

        Boolean presetOnly = preset != null && preset ? true : null;
        Page<DeckSummary> deckPage = deckService.getAllDecks(calculatedPage, limit, archetype, presetOnly);

        PaginationResponse pagination = new PaginationResponse(
            calculatedPage,
            limit,
            deckPage.getTotalElements(),
            deckPage.getTotalPages()
        );

        Map<String, Object> response = new HashMap<>();
        response.put("decks", deckPage.getContent());
        response.put("pagination", pagination);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get deck by ID", description = "Get detailed information about a specific deck with all cards")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Deck found",
            content = @Content(schema = @Schema(implementation = DeckWithCards.class))),
        @ApiResponse(responseCode = "404", description = "Deck not found")
    })
    public ResponseEntity<DeckWithCards> getDeckById(
            @Parameter(description = "Deck ID", required = true)
            @PathVariable Integer id) {

        Optional<DeckWithCards> deck = deckService.getDeckById(id);
        return deck.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
