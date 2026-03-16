"""Tests for generate_cards_csv module."""
import sys
from pathlib import Path

import pytest

from src import generate_cards_csv


def test_default_card_iconic():
    """default_card returns iconic data for known IDs."""
    result = generate_cards_csv.default_card(1, "Blue-Eyes White Dragon")
    assert result["id"] == 1
    assert result["name"] == "Blue-Eyes White Dragon"
    assert result["type"] == "Normal Monster"
    assert result["attribute"] == "LIGHT"
    assert result["race"] == "Dragon"
    assert result["level"] == 8
    assert result["attack_points"] == 3000
    assert result["defense_points"] == 2500
    assert result["cost"] == 8
    assert "description" in result
    assert "image" in result


def test_default_card_uses_name_not_id():
    """default_card uses name-based lookup, so card 2 (Mystical Elf) gets correct data."""
    result = generate_cards_csv.default_card(2, "Mystical Elf")
    assert result["name"] == "Mystical Elf"
    assert "15025844" in result["image"]
    assert result["attack_points"] == 800
    assert result["defense_points"] == 2000


def test_default_card_generic():
    """default_card returns generated data for unknown IDs."""
    result = generate_cards_csv.default_card(99, "Generic Card")
    assert result["id"] == 99
    assert result["name"] == "Generic Card"
    assert result["type"] == "Normal Monster"
    assert result["level"] in (3, 4, 5, 6)
    assert result["attack_points"] >= 1200
    assert result["defense_points"] >= 1000
    assert result["cost"] == result["level"]
    assert result["attribute"] in ("DARK", "LIGHT", "EARTH", "WATER", "FIRE", "WIND")
    assert result["race"] in ("Dragon", "Spellcaster", "Warrior", "Fiend", "Beast", "Machine")


def test_default_card_variety():
    """default_card produces varied stats for different IDs."""
    r1 = generate_cards_csv.default_card(11, "A")
    r2 = generate_cards_csv.default_card(12, "B")
    # Different IDs should give different attributes/races (id % 6)
    assert (r1["attribute"], r1["race"]) != (r2["attribute"], r2["race"]) or r1["level"] != r2["level"]


def test_main_creates_cards_csv(tmp_path, monkeypatch):
    """main reads card_list and writes cards.csv."""
    card_list = tmp_path / "card_list.csv"
    card_list.write_text("id,name\n1,Blue-Eyes\n2,Dark Magician")
    cards_out = tmp_path / "cards.csv"

    monkeypatch.setattr(sys, "argv", ["generate_cards_csv.py"])
    monkeypatch.setattr(generate_cards_csv, "CARD_LIST", card_list)
    monkeypatch.setattr(generate_cards_csv, "CARDS_OUT", cards_out)

    generate_cards_csv.main()

    assert cards_out.exists()
    content = cards_out.read_text()
    assert "id,name,type,attribute" in content
    assert "Blue-Eyes" in content
    assert "Dark Magician" in content


def test_main_missing_card_list(tmp_path, monkeypatch, capsys):
    """main exits when card_list.csv not found."""
    monkeypatch.setattr(sys, "argv", ["generate_cards_csv.py"])
    monkeypatch.setattr(generate_cards_csv, "CARD_LIST", tmp_path / "nonexistent.csv")
    monkeypatch.setattr(generate_cards_csv, "CARDS_OUT", tmp_path / "out.csv")
    with pytest.raises(SystemExit):
        generate_cards_csv.main()
    captured = capsys.readouterr()
    assert "not found" in (captured.err + captured.out)
