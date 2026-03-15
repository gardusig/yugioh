-- Enforce non-negative attack and defense points (game uses 0 for "?" or N/A)
UPDATE cards SET attack_points = 0 WHERE attack_points < 0;
UPDATE cards SET defense_points = 0 WHERE defense_points < 0;
ALTER TABLE cards
  ADD CONSTRAINT chk_cards_attack_non_negative CHECK (attack_points >= 0),
  ADD CONSTRAINT chk_cards_defense_non_negative CHECK (defense_points >= 0);
