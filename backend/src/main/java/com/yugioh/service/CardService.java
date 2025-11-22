package com.yugioh.service;

import com.yugioh.model.Card;
import com.yugioh.repository.CardRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

import jakarta.persistence.criteria.Predicate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class CardService {
    @Autowired
    private CardRepository cardRepository;

    public Page<Card> getAllCards(int page, int limit, Integer startId) {
        Pageable pageable = PageRequest.of(page - 1, limit, Sort.by("id").ascending());

        if (startId != null && startId > 0) {
            // Filter cards starting from startId
            Specification<Card> spec = (root, query, cb) -> {
                List<Predicate> predicates = new ArrayList<>();
                predicates.add(cb.greaterThanOrEqualTo(root.get("id"), startId));
                return cb.and(predicates.toArray(new Predicate[0]));
            };
            return cardRepository.findAll(spec, pageable);
        }

        return cardRepository.findAll(pageable);
    }

    public Optional<Card> getCardById(Integer id) {
        return cardRepository.findById(id);
    }

    public List<Card> getCardsByIds(List<Integer> ids) {
        return cardRepository.findByIds(ids);
    }
}
