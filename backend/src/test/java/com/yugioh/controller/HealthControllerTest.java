package com.yugioh.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(MockitoExtension.class)
@DisplayName("HealthController Tests")
class HealthControllerTest {

    @InjectMocks
    private HealthController healthController;

    @Test
    @DisplayName("Should return healthy status")
    void healthCheck_ReturnsHealthyStatus() {
        // When
        ResponseEntity<Map<String, String>> response = healthController.healthCheck();

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().get("status")).isEqualTo("healthy");
    }

    @Test
    @DisplayName("Should return response with correct structure")
    void healthCheck_ReturnsCorrectStructure() {
        // When
        ResponseEntity<Map<String, String>> response = healthController.healthCheck();

        // Then
        assertThat(response.getBody()).isInstanceOf(Map.class);
        assertThat(response.getBody().size()).isEqualTo(1);
        assertThat(response.getBody().containsKey("status")).isTrue();
    }
}
