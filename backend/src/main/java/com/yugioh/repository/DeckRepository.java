package com.yugioh.repository;

import com.yugioh.model.Deck;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface DeckRepository extends JpaRepository<Deck, Integer> {
    @Query("SELECT d FROM Deck d WHERE " +
        "(:archetype IS NULL OR d.archetype = :archetype) AND " +
        "(:presetOnly IS NULL OR d.isPreset = :presetOnly)")
    Page<Deck> findAllWithFilters(
        @Param("archetype") String archetype,
        @Param("presetOnly") Boolean presetOnly,
        Pageable pageable
    );

    @Query("SELECT COUNT(d) FROM Deck d WHERE " +
        "d.id < :deckId AND " +
        "(:archetype IS NULL OR d.archetype = :archetype) AND " +
        "(:presetOnly IS NULL OR d.isPreset = :presetOnly)")
    long countDecksBeforeId(
        @Param("deckId") Integer deckId,
        @Param("archetype") String archetype,
        @Param("presetOnly") Boolean presetOnly
    );
}
