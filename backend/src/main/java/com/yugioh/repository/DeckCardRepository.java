package com.yugioh.repository;

import com.yugioh.model.DeckCard;
import com.yugioh.model.DeckCardId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DeckCardRepository extends JpaRepository<DeckCard, DeckCardId> {
    @Query("SELECT dc.cardId FROM DeckCard dc WHERE dc.deckId = :deckId ORDER BY dc.position")
    List<Integer> findCardIdsByDeckId(@Param("deckId") Integer deckId);
}
