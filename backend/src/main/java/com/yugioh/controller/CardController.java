package com.yugioh.controller;

import com.yugioh.dto.PaginationResponse;
import com.yugioh.model.Card;
import com.yugioh.service.CardService;
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
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/cards")
@CrossOrigin(origins = "*")
@Tag(name = "Cards", description = "API for browsing all 900 cards from Yu-Gi-Oh! The Sacred Cards")
public class CardController {
    @Autowired
    private CardService cardService;

    @GetMapping
    @Operation(summary = "List all cards", description = "Get a paginated list of all cards (001-900). Use either 'page' or 'firstCard' query parameter.")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Successful response",
            content = @Content(schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> getAllCards(
            @Parameter(description = "Page number (1-based). Ignored if firstCard is provided.", example = "1")
            @RequestParam(required = false) Integer page,
            @Parameter(description = "Number of cards per page", example = "24")
            @RequestParam(defaultValue = "24") int limit,
            @Parameter(description = "First card ID to start from (1-900). Takes precedence over page.", example = "1")
            @RequestParam(required = false) Integer firstCard) {

        // When firstCard is provided, filter from that card and use page 1 of filtered results
        // Otherwise, use the page parameter (default to 1)
        int calculatedPage = 1;
        Integer startId = null;
        if (firstCard != null && firstCard > 0) {
            // When filtering by firstCard, always start at page 1 of the filtered results
            calculatedPage = 1;
            startId = firstCard;
        } else if (page != null && page > 0) {
            calculatedPage = page;
        }

        Page<Card> cardPage = cardService.getAllCards(calculatedPage, limit, startId);
        List<Card> cards = cardPage.getContent();

        PaginationResponse pagination = new PaginationResponse(
            calculatedPage,
            limit,
            cardPage.getTotalElements(),
            cardPage.getTotalPages()
        );

        Map<String, Object> response = new HashMap<>();
        response.put("cards", cards);
        response.put("pagination", pagination);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get card by ID", description = "Get detailed information about a specific card")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Card found",
            content = @Content(schema = @Schema(implementation = Card.class))),
        @ApiResponse(responseCode = "404", description = "Card not found")
    })
    public ResponseEntity<Card> getCardById(
            @Parameter(description = "Card ID (001-900)", required = true)
            @PathVariable Integer id) {

        Optional<Card> card = cardService.getCardById(id);
        return card.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
