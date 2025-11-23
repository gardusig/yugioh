package com.yugioh.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@DisplayName("OpenApiConfig Tests")
class OpenApiConfigTest {

    @Autowired
    private OpenAPI openAPI;

    @Test
    @DisplayName("Should create OpenAPI bean with correct configuration")
    void customOpenAPI_ShouldHaveCorrectConfiguration() {
        // Then
        assertThat(openAPI).isNotNull();

        Info info = openAPI.getInfo();
        assertThat(info).isNotNull();
        assertThat(info.getTitle()).isEqualTo("Yu-Gi-Oh! The Sacred Cards API");
        assertThat(info.getVersion()).isEqualTo("1.0.0");
        assertThat(info.getDescription()).contains("API for browsing all 900 cards");
        assertThat(info.getContact()).isNotNull();
        assertThat(info.getContact().getName()).isEqualTo("Yu-Gi-Oh! API");
        assertThat(info.getContact().getEmail()).isEqualTo("api@yugioh.com");

        List<Server> servers = openAPI.getServers();
        assertThat(servers).isNotNull();
        assertThat(servers).hasSize(2);
        assertThat(servers.get(0).getUrl()).isEqualTo("http://localhost:8080");
        assertThat(servers.get(0).getDescription()).isEqualTo("Local development server");
        assertThat(servers.get(1).getUrl()).isEqualTo("http://backend:8080");
        assertThat(servers.get(1).getDescription()).isEqualTo("Docker container server");
    }
}
