package com.yugioh.dto;

public class DeckSummary {
    private Integer id;
    private String name;
    private String description;
    private String characterName;
    private String archetype;
    private String mostCommonType;
    private Integer maxCost;
    private Integer totalCost;
    private Integer cardCount;
    private Boolean isPreset;

    public DeckSummary() {}

    public DeckSummary(Integer id, String name, String description, String characterName,
                    String archetype, String mostCommonType, Integer maxCost, Integer totalCost,
                    Integer cardCount, Boolean isPreset) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.characterName = characterName;
        this.archetype = archetype;
        this.mostCommonType = mostCommonType;
        this.maxCost = maxCost;
        this.totalCost = totalCost;
        this.cardCount = cardCount;
        this.isPreset = isPreset;
    }

    // Getters and Setters
    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCharacterName() {
        return characterName;
    }

    public void setCharacterName(String characterName) {
        this.characterName = characterName;
    }

    public String getArchetype() {
        return archetype;
    }

    public void setArchetype(String archetype) {
        this.archetype = archetype;
    }

    public String getMostCommonType() {
        return mostCommonType;
    }

    public void setMostCommonType(String mostCommonType) {
        this.mostCommonType = mostCommonType;
    }

    public Integer getMaxCost() {
        return maxCost;
    }

    public void setMaxCost(Integer maxCost) {
        this.maxCost = maxCost;
    }

    public Integer getTotalCost() {
        return totalCost;
    }

    public void setTotalCost(Integer totalCost) {
        this.totalCost = totalCost;
    }

    public Integer getCardCount() {
        return cardCount;
    }

    public void setCardCount(Integer cardCount) {
        this.cardCount = cardCount;
    }

    public Boolean getIsPreset() {
        return isPreset;
    }

    public void setIsPreset(Boolean isPreset) {
        this.isPreset = isPreset;
    }
}
