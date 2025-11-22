package com.yugioh.dto;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("PaginationResponse Tests")
class PaginationResponseTest {

    @Test
    @DisplayName("Should create PaginationResponse with no-args constructor")
    void constructor_NoArgs_CreatesEmptyObject() {
        // When
        PaginationResponse response = new PaginationResponse();

        // Then
        assertThat(response).isNotNull();
        assertThat(response.getPage()).isNull();
        assertThat(response.getLimit()).isNull();
        assertThat(response.getTotal()).isNull();
        assertThat(response.getTotalPages()).isNull();
    }

    @Test
    @DisplayName("Should create PaginationResponse with all parameters")
    void constructor_WithAllParams_SetsAllFields() {
        // Given
        Integer page = 1;
        Integer limit = 24;
        Long total = 100L;
        Integer totalPages = 5;

        // When
        PaginationResponse response = new PaginationResponse(page, limit, total, totalPages);

        // Then
        assertThat(response.getPage()).isEqualTo(page);
        assertThat(response.getLimit()).isEqualTo(limit);
        assertThat(response.getTotal()).isEqualTo(total);
        assertThat(response.getTotalPages()).isEqualTo(totalPages);
    }

    @Test
    @DisplayName("Should set and get page")
    void setPage_AndGetPage_WorksCorrectly() {
        // Given
        PaginationResponse response = new PaginationResponse();
        Integer page = 2;

        // When
        response.setPage(page);

        // Then
        assertThat(response.getPage()).isEqualTo(page);
    }

    @Test
    @DisplayName("Should set and get limit")
    void setLimit_AndGetLimit_WorksCorrectly() {
        // Given
        PaginationResponse response = new PaginationResponse();
        Integer limit = 50;

        // When
        response.setLimit(limit);

        // Then
        assertThat(response.getLimit()).isEqualTo(limit);
    }

    @Test
    @DisplayName("Should set and get total")
    void setTotal_AndGetTotal_WorksCorrectly() {
        // Given
        PaginationResponse response = new PaginationResponse();
        Long total = 200L;

        // When
        response.setTotal(total);

        // Then
        assertThat(response.getTotal()).isEqualTo(total);
    }

    @Test
    @DisplayName("Should set and get totalPages")
    void setTotalPages_AndGetTotalPages_WorksCorrectly() {
        // Given
        PaginationResponse response = new PaginationResponse();
        Integer totalPages = 10;

        // When
        response.setTotalPages(totalPages);

        // Then
        assertThat(response.getTotalPages()).isEqualTo(totalPages);
    }
}
