package com.yugioh.repository;

import com.yugioh.model.Card;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CardRepository extends JpaRepository<Card, Integer>, JpaSpecificationExecutor<Card> {
    @Query("SELECT c FROM Card c WHERE c.id IN :ids ORDER BY c.id")
    List<Card> findByIds(@Param("ids") List<Integer> ids);
}
