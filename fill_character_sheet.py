#!/usr/bin/env python3
"""
D&D 5e Character Sheet PDF Filler

This script takes a structured Character.json file and fills out a 
D&D 5e character sheet PDF (AcroForm) using the data and D&D 5e rules.
"""

import json
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter


# ==============================================================================
# D&D 5e Rule Helper Functions
# ==============================================================================

def ability_modifier(score):
    """
    Calculate ability modifier from ability score.
    Formula: (score - 10) // 2
    """
    return (score - 10) // 2


def proficiency_bonus(level):
    """
    Calculate proficiency bonus based on total character level.
    Level 1-4: +2
    Level 5-8: +3
    Level 9-12: +4
    Level 13-16: +5
    Level 17-20: +6
    """
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6


def saving_throw_bonus(ability_mod, is_proficient, prof_bonus):
    """
    Calculate saving throw bonus.
    Formula: ability_modifier + proficiency_bonus (if proficient)
    """
    bonus = ability_mod
    if is_proficient:
        bonus += prof_bonus
    return bonus


def skill_bonus(ability_mod, is_proficient, prof_bonus):
    """
    Calculate skill bonus.
    Formula: ability_modifier + proficiency_bonus (if proficient)
    """
    bonus = ability_mod
    if is_proficient:
        bonus += prof_bonus
    return bonus


def initiative_bonus(dex_mod):
    """
    Calculate initiative bonus.
    Formula: DEX modifier
    """
    return dex_mod


def passive_perception(perception_bonus):
    """
    Calculate Passive Perception.
    Formula: 10 + Perception skill bonus
    """
    return 10 + perception_bonus


def spell_save_dc(prof_bonus, spellcasting_mod):
    """
    Calculate spell save DC.
    Formula: 8 + proficiency_bonus + spellcasting_ability_modifier
    """
    return 8 + prof_bonus + spellcasting_mod


def spell_attack_bonus(prof_bonus, spellcasting_mod):
    """
    Calculate spell attack bonus.
    Formula: proficiency_bonus + spellcasting_ability_modifier
    """
    return prof_bonus + spellcasting_mod


# ==============================================================================
# Skill to Ability Mapping
# ==============================================================================

SKILL_ABILITY_MAP = {
    "Acrobatics": "DEX",
    "Animal Handling": "WIS",
    "Arcana": "INT",
    "Athletics": "STR",
    "Deception": "CHA",
    "History": "INT",
    "Insight": "WIS",
    "Intimidation": "CHA",
    "Investigation": "INT",
    "Medicine": "WIS",
    "Nature": "INT",
    "Perception": "WIS",
    "Performance": "CHA",
    "Persuasion": "CHA",
    "Religion": "INT",
    "Sleight of Hand": "DEX",
    "Stealth": "DEX",
    "Survival": "WIS"
}


# ==============================================================================
# Main PDF Filling Logic
# ==============================================================================

def load_character_data(json_path):
    """Load character data from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def format_bonus(value):
    """Format a bonus value with + or - sign."""
    if value >= 0:
        return f"+{value}"
    else:
        return str(value)


def compute_derived_stats(character):
    """
    Compute all derived stats from character data using D&D 5e rules.
    Returns a dictionary of computed values.
    """
    # Get ability scores
    ability_scores = character['ability_scores']
    
    # Calculate ability modifiers
    modifiers = {
        ability: ability_modifier(score)
        for ability, score in ability_scores.items()
    }
    
    # Calculate total level
    total_level = sum(cls['level'] for cls in character['classes'])
    
    # Calculate proficiency bonus
    prof_bonus = proficiency_bonus(total_level)
    
    # Calculate saving throws
    saving_throws = {}
    for ability in ability_scores.keys():
        is_proficient = character['saving_throws'].get(ability, False)
        saving_throws[ability] = saving_throw_bonus(
            modifiers[ability], is_proficient, prof_bonus
        )
    
    # Calculate skill bonuses
    skills = {}
    for skill_name, is_proficient in character['skills'].items():
        ability = SKILL_ABILITY_MAP[skill_name]
        skills[skill_name] = skill_bonus(
            modifiers[ability], is_proficient, prof_bonus
        )
    
    # Calculate initiative
    initiative = initiative_bonus(modifiers['DEX'])
    
    # Calculate passive perception
    perception_bonus = skills.get('Perception', modifiers['WIS'])
    passive_perc = passive_perception(perception_bonus)
    
    # Calculate spellcasting stats (if applicable)
    spell_dc = None
    spell_atk = None
    spellcasting_ability = None
    
    for cls in character['classes']:
        if cls.get('spellcasting_stat'):
            spellcasting_ability = cls['spellcasting_stat']
            spellcasting_mod = modifiers[spellcasting_ability]
            spell_dc = spell_save_dc(prof_bonus, spellcasting_mod)
            spell_atk = spell_attack_bonus(prof_bonus, spellcasting_mod)
            break
    
    return {
        'modifiers': modifiers,
        'proficiency_bonus': prof_bonus,
        'saving_throws': saving_throws,
        'skills': skills,
        'initiative': initiative,
        'passive_perception': passive_perc,
        'spell_save_dc': spell_dc,
        'spell_attack_bonus': spell_atk,
        'spellcasting_ability': spellcasting_ability,
        'total_level': total_level
    }


def fill_character_sheet(input_pdf_path, output_pdf_path, character_data):
    """
    Fill the character sheet PDF with data from character_data.
    """
    # Load the PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Compute derived stats
    derived = compute_derived_stats(character_data)
    
    # Create field mapping dictionary
    field_values = {}
    
    # Basic Identity Fields
    field_values['CharacterName'] = character_data['name']
    field_values['PlayerName'] = character_data['player']['name']
    field_values['Race'] = character_data['race']['name']
    field_values['Alignment'] = character_data['alignment']
    
    # Class and Level (combine if single class)
    classes_str = ', '.join([
        f"{cls['name']} {cls['level']}" 
        for cls in character_data['classes']
    ])
    field_values['ClassLevel'] = classes_str
    
    # Ability Scores
    for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
        score = character_data['ability_scores'][ability]
        modifier = derived['modifiers'][ability]
        
        field_values[ability] = str(score)
        field_values[f"{ability}mod"] = format_bonus(modifier)
    
    # Proficiency Bonus
    field_values['ProfBonus'] = format_bonus(derived['proficiency_bonus'])
    
    # Saving Throws
    for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
        save_bonus = derived['saving_throws'][ability]
        field_values[f"ST {ability}"] = format_bonus(save_bonus)
        
        # Mark proficiency checkbox if proficient
        if character_data['saving_throws'].get(ability, False):
            field_values[f"Check Box {ability}"] = True
    
    # Skills
    skill_field_names = {
        "Acrobatics": "Acrobatics",
        "Animal Handling": "Animal",
        "Arcana": "Arcana",
        "Athletics": "Athletics",
        "Deception": "Deception",
        "History": "History",
        "Insight": "Insight",
        "Intimidation": "Intimidation",
        "Investigation": "Investigation",
        "Medicine": "Medicine",
        "Nature": "Nature",
        "Perception": "Perception",
        "Performance": "Performance",
        "Persuasion": "Persuasion",
        "Religion": "Religion",
        "Sleight of Hand": "SleightofHand",
        "Stealth": "Stealth",
        "Survival": "Survival"
    }
    
    for skill_name, field_name in skill_field_names.items():
        skill_value = derived['skills'].get(skill_name, 0)
        field_values[field_name] = format_bonus(skill_value)
        
        # Mark proficiency checkbox if proficient
        if character_data['skills'].get(skill_name, False):
            field_values[f"Check Box {field_name}"] = True
    
    # Combat Stats
    field_values['AC'] = str(character_data['armor_class']['value'])
    field_values['Initiative'] = format_bonus(derived['initiative'])
    field_values['Speed'] = str(character_data['speed'].get('Walk', 30))
    field_values['HPMax'] = str(character_data['hit_points']['max'])
    field_values['HPCurrent'] = str(character_data['hit_points']['current'])
    
    # Passive Perception
    field_values['Passive'] = str(derived['passive_perception'])
    
    # Personality Traits
    details = character_data.get('details', {})
    field_values['PersonalityTraits'] = details.get('personality', '')
    field_values['Ideals'] = details.get('ideal', '')
    field_values['Bonds'] = details.get('bond', '')
    field_values['Flaws'] = details.get('flaw', '')
    
    # Weapons (up to 2)
    weapons = character_data.get('weapons', [])
    for i, weapon in enumerate(weapons[:2], start=1):
        field_values[f"Wpn Name {i}"] = weapon['name']
        field_values[f"Wpn{i} AtkBonus"] = format_bonus(weapon.get('attack_bonus', 0))
        damage = weapon.get('damage', '')
        damage_type = weapon.get('damage_type', '')
        field_values[f"Wpn{i} Damage"] = f"{damage} {damage_type}"
    
    # Spellcasting
    if derived['spell_save_dc'] is not None:
        field_values['SpellcastingClass'] = character_data['classes'][0]['name']
        field_values['SpellcastingAbility'] = derived['spellcasting_ability']
        field_values['SpellSaveDC'] = str(derived['spell_save_dc'])
        field_values['SpellAtkBonus'] = format_bonus(derived['spell_attack_bonus'])
    
    # Copy all pages from the input PDF
    for page in reader.pages:
        writer.add_page(page)
    
    # Update form fields
    writer.update_page_form_field_values(
        writer.pages[0],
        field_values
    )
    
    # Write the output PDF
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"Successfully created filled character sheet: {output_pdf_path}")
    return field_values


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python fill_character_sheet.py <input_pdf> <character_json> [output_pdf]")
        print("\nExample:")
        print("  python fill_character_sheet.py character_sheet.pdf Character.json filled_character.pdf")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    character_json = sys.argv[2]
    output_pdf = sys.argv[3] if len(sys.argv) > 3 else "filled_character.pdf"
    
    # Validate input files exist
    if not Path(input_pdf).exists():
        print(f"Error: Input PDF not found: {input_pdf}")
        sys.exit(1)
    
    if not Path(character_json).exists():
        print(f"Error: Character JSON not found: {character_json}")
        sys.exit(1)
    
    # Load character data
    print(f"Loading character data from {character_json}...")
    character = load_character_data(character_json)
    
    # Fill the character sheet
    print(f"Filling character sheet from {input_pdf}...")
    fill_character_sheet(input_pdf, output_pdf, character)


if __name__ == "__main__":
    main()
