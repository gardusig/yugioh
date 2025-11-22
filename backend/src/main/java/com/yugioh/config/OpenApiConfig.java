package com.yugioh.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Yu-Gi-Oh! The Sacred Cards API")
                .version("1.0.0")
                .description("API for browsing all 900 cards and character decks from Yu-Gi-Oh! The Sacred Cards")
                .contact(new Contact()
                    .name("Yu-Gi-Oh! API")
                    .email("api@yugioh.com")))
            .servers(List.of(
                new Server().url("http://localhost:8080").description("Local development server"),
                new Server().url("http://backend:8080").description("Docker container server")
            ));
    }
}
