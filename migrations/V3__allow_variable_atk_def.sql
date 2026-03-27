-- Allow -1 for variable ATK/DEF (e.g. Slifer, Ra use "?" in the game)
ALTER TABLE cards DROP CONSTRAINT IF EXISTS chk_cards_attack_non_negative;
ALTER TABLE cards DROP CONSTRAINT IF EXISTS chk_cards_defense_non_negative;
ALTER TABLE cards
  ADD CONSTRAINT chk_cards_attack_non_negative CHECK (attack_points >= -1),
  ADD CONSTRAINT chk_cards_defense_non_negative CHECK (defense_points >= -1);
