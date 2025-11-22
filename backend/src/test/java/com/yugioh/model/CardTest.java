package com.yugioh.model;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("Card Model Tests")
class CardTest {

    private Card card;

    @BeforeEach
    void setUp() {
        card = new Card();
    }

    @Test
    @DisplayName("Should set and get id")
    void setId_And_GetId() {
        Integer id = 1;
        card.setId(id);
        assertThat(card.getId()).isEqualTo(id);
    }

    @Test
    @DisplayName("Should set and get name")
    void setName_And_GetName() {
        String name = "Blue-Eyes White Dragon";
        card.setName(name);
        assertThat(card.getName()).isEqualTo(name);
    }

    @Test
    @DisplayName("Should set and get description")
    void setDescription_And_GetDescription() {
        String description = "A legendary dragon";
        card.setDescription(description);
        assertThat(card.getDescription()).isEqualTo(description);
    }

    @Test
    @DisplayName("Should set and get image")
    void setImage_And_GetImage() {
        String image = "http://example.com/image.png";
        card.setImage(image);
        assertThat(card.getImage()).isEqualTo(image);
    }

    @Test
    @DisplayName("Should set and get type")
    void setType_And_GetType() {
        String type = "Monster";
        card.setType(type);
        assertThat(card.getType()).isEqualTo(type);
    }

    @Test
    @DisplayName("Should set and get attribute")
    void setAttribute_And_GetAttribute() {
        String attribute = "Light";
        card.setAttribute(attribute);
        assertThat(card.getAttribute()).isEqualTo(attribute);
    }

    @Test
    @DisplayName("Should set and get race")
    void setRace_And_GetRace() {
        String race = "Dragon";
        card.setRace(race);
        assertThat(card.getRace()).isEqualTo(race);
    }

    @Test
    @DisplayName("Should set and get level")
    void setLevel_And_GetLevel() {
        Integer level = 8;
        card.setLevel(level);
        assertThat(card.getLevel()).isEqualTo(level);
    }

    @Test
    @DisplayName("Should set and get attack points")
    void setAttackPoints_And_GetAttackPoints() {
        Integer attackPoints = 3000;
        card.setAttackPoints(attackPoints);
        assertThat(card.getAttackPoints()).isEqualTo(attackPoints);
    }

    @Test
    @DisplayName("Should set and get defense points")
    void setDefensePoints_And_GetDefensePoints() {
        Integer defensePoints = 2500;
        card.setDefensePoints(defensePoints);
        assertThat(card.getDefensePoints()).isEqualTo(defensePoints);
    }

    @Test
    @DisplayName("Should set and get cost")
    void setCost_And_GetCost() {
        Integer cost = 8;
        card.setCost(cost);
        assertThat(card.getCost()).isEqualTo(cost);
    }

    @Test
    @DisplayName("Should set and get rarity")
    void setRarity_And_GetRarity() {
        String rarity = "Ultra Rare";
        card.setRarity(rarity);
        assertThat(card.getRarity()).isEqualTo(rarity);
    }

    @Test
    @DisplayName("Should set and get created at")
    void setCreatedAt_And_GetCreatedAt() {
        LocalDateTime createdAt = LocalDateTime.now();
        card.setCreatedAt(createdAt);
        assertThat(card.getCreatedAt()).isEqualTo(createdAt);
    }

    @Test
    @DisplayName("Should set and get updated at")
    void setUpdatedAt_And_GetUpdatedAt() {
        LocalDateTime updatedAt = LocalDateTime.now();
        card.setUpdatedAt(updatedAt);
        assertThat(card.getUpdatedAt()).isEqualTo(updatedAt);
    }
}
