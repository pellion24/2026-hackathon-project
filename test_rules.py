#!/usr/bin/env python3
"""
Test script for D&D 5e rule helper functions.
Validates that the calculations follow D&D 5e rules correctly.
"""

from fill_character_sheet import (
    ability_modifier,
    proficiency_bonus,
    saving_throw_bonus,
    skill_bonus,
    initiative_bonus,
    passive_perception,
    spell_save_dc,
    spell_attack_bonus,
    compute_derived_stats
)


def test_ability_modifier():
    """Test ability modifier calculations."""
    print("Testing ability_modifier()...")
    
    # Test standard ability scores
    assert ability_modifier(10) == 0, "10 should give +0"
    assert ability_modifier(11) == 0, "11 should give +0"
    assert ability_modifier(12) == 1, "12 should give +1"
    assert ability_modifier(8) == -1, "8 should give -1"
    assert ability_modifier(20) == 5, "20 should give +5"
    assert ability_modifier(3) == -4, "3 should give -4"
    
    print("  ✓ All ability modifier tests passed")


def test_proficiency_bonus():
    """Test proficiency bonus calculations."""
    print("Testing proficiency_bonus()...")
    
    assert proficiency_bonus(1) == 2, "Level 1 should give +2"
    assert proficiency_bonus(4) == 2, "Level 4 should give +2"
    assert proficiency_bonus(5) == 3, "Level 5 should give +3"
    assert proficiency_bonus(8) == 3, "Level 8 should give +3"
    assert proficiency_bonus(9) == 4, "Level 9 should give +4"
    assert proficiency_bonus(12) == 4, "Level 12 should give +4"
    assert proficiency_bonus(13) == 5, "Level 13 should give +5"
    assert proficiency_bonus(16) == 5, "Level 16 should give +5"
    assert proficiency_bonus(17) == 6, "Level 17 should give +6"
    assert proficiency_bonus(20) == 6, "Level 20 should give +6"
    
    print("  ✓ All proficiency bonus tests passed")


def test_saving_throw_bonus():
    """Test saving throw bonus calculations."""
    print("Testing saving_throw_bonus()...")
    
    # With proficiency
    assert saving_throw_bonus(3, True, 2) == 5, "Should add prof bonus when proficient"
    # Without proficiency
    assert saving_throw_bonus(3, False, 2) == 3, "Should not add prof bonus when not proficient"
    # Negative modifier
    assert saving_throw_bonus(-1, True, 2) == 1, "Should handle negative modifiers"
    
    print("  ✓ All saving throw bonus tests passed")


def test_skill_bonus():
    """Test skill bonus calculations."""
    print("Testing skill_bonus()...")
    
    # Same logic as saving throws
    assert skill_bonus(3, True, 2) == 5, "Should add prof bonus when proficient"
    assert skill_bonus(3, False, 2) == 3, "Should not add prof bonus when not proficient"
    
    print("  ✓ All skill bonus tests passed")


def test_initiative_bonus():
    """Test initiative bonus calculations."""
    print("Testing initiative_bonus()...")
    
    assert initiative_bonus(2) == 2, "Initiative should equal DEX modifier"
    assert initiative_bonus(-1) == -1, "Initiative should handle negative modifiers"
    
    print("  ✓ All initiative bonus tests passed")


def test_passive_perception():
    """Test passive perception calculations."""
    print("Testing passive_perception()...")
    
    assert passive_perception(3) == 13, "PP should be 10 + perception bonus"
    assert passive_perception(0) == 10, "PP with 0 bonus should be 10"
    assert passive_perception(-1) == 9, "PP should handle negative bonuses"
    
    print("  ✓ All passive perception tests passed")


def test_spell_save_dc():
    """Test spell save DC calculations."""
    print("Testing spell_save_dc()...")
    
    assert spell_save_dc(2, 3) == 13, "DC should be 8 + prof + modifier"
    assert spell_save_dc(3, 4) == 15, "DC should be 8 + prof + modifier"
    
    print("  ✓ All spell save DC tests passed")


def test_spell_attack_bonus():
    """Test spell attack bonus calculations."""
    print("Testing spell_attack_bonus()...")
    
    assert spell_attack_bonus(2, 3) == 5, "Attack should be prof + modifier"
    assert spell_attack_bonus(3, 4) == 7, "Attack should be prof + modifier"
    
    print("  ✓ All spell attack bonus tests passed")


def test_compute_derived_stats():
    """Test full derived stats computation."""
    print("Testing compute_derived_stats()...")
    
    # Create a test character
    test_character = {
        "ability_scores": {
            "STR": 16,
            "DEX": 12,
            "CON": 15,
            "INT": 10,
            "WIS": 13,
            "CHA": 8
        },
        "classes": [
            {
                "name": "Fighter",
                "level": 3,
                "hit_die": "d10",
                "spellcasting_stat": None
            }
        ],
        "saving_throws": {
            "STR": True,
            "DEX": False,
            "CON": True,
            "INT": False,
            "WIS": False,
            "CHA": False
        },
        "skills": {
            "Acrobatics": False,
            "Animal Handling": False,
            "Arcana": False,
            "Athletics": True,
            "Deception": False,
            "History": False,
            "Insight": False,
            "Intimidation": True,
            "Investigation": False,
            "Medicine": False,
            "Nature": False,
            "Perception": True,
            "Performance": False,
            "Persuasion": False,
            "Religion": False,
            "Sleight of Hand": False,
            "Stealth": False,
            "Survival": False
        }
    }
    
    derived = compute_derived_stats(test_character)
    
    # Check ability modifiers
    assert derived['modifiers']['STR'] == 3, "STR 16 should give +3"
    assert derived['modifiers']['DEX'] == 1, "DEX 12 should give +1"
    assert derived['modifiers']['CON'] == 2, "CON 15 should give +2"
    assert derived['modifiers']['INT'] == 0, "INT 10 should give +0"
    assert derived['modifiers']['WIS'] == 1, "WIS 13 should give +1"
    assert derived['modifiers']['CHA'] == -1, "CHA 8 should give -1"
    
    # Check proficiency bonus
    assert derived['proficiency_bonus'] == 2, "Level 3 should give +2 prof"
    
    # Check saving throws
    assert derived['saving_throws']['STR'] == 5, "STR save should be +5 (3+2)"
    assert derived['saving_throws']['DEX'] == 1, "DEX save should be +1 (no prof)"
    assert derived['saving_throws']['CON'] == 4, "CON save should be +4 (2+2)"
    
    # Check skills
    assert derived['skills']['Athletics'] == 5, "Athletics should be +5 (3+2)"
    assert derived['skills']['Intimidation'] == 1, "Intimidation should be +1 (-1+2)"
    assert derived['skills']['Perception'] == 3, "Perception should be +3 (1+2)"
    assert derived['skills']['Acrobatics'] == 1, "Acrobatics should be +1 (no prof)"
    
    # Check initiative
    assert derived['initiative'] == 1, "Initiative should be +1 (DEX mod)"
    
    # Check passive perception
    assert derived['passive_perception'] == 13, "PP should be 13 (10+3)"
    
    # Check total level
    assert derived['total_level'] == 3, "Total level should be 3"
    
    print("  ✓ All derived stats tests passed")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*60)
    print("Running D&D 5e Rule Helper Function Tests")
    print("="*60 + "\n")
    
    test_ability_modifier()
    test_proficiency_bonus()
    test_saving_throw_bonus()
    test_skill_bonus()
    test_initiative_bonus()
    test_passive_perception()
    test_spell_save_dc()
    test_spell_attack_bonus()
    test_compute_derived_stats()
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
