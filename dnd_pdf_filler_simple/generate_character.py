"""
D&D 5e Character Sheet PDF Filler - Complete MVP with CLI
Fills all available fields in the official D&D 5e character sheet PDF
"""

import json
import argparse
import sys
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject


# ============================================================================
# D&D 5E RULES - CALCULATIONS
# ============================================================================

def ability_mod(score):
    """Calculate ability modifier from ability score"""
    return (score - 10) // 2


def prof_bonus(level):
    """Calculate proficiency bonus from character level"""
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


def skill_bonus(ability_mod, prof_bonus, is_proficient):
    """Calculate skill bonus"""
    return ability_mod + (prof_bonus if is_proficient else 0)


def saving_throw_bonus(ability_mod, prof_bonus, is_proficient):
    """Calculate saving throw bonus"""
    return ability_mod + (prof_bonus if is_proficient else 0)


def passive_perception(perception_bonus):
    """Calculate passive perception"""
    return 10 + perception_bonus


def format_modifier(value):
    """Format modifier with + or - sign"""
    return f"+{value}" if value >= 0 else str(value)


# ============================================================================
# SPELL CALCULATIONS (CRITICAL)
# ============================================================================

def calculate_spells_known(class_name, level, spellcasting_ability_modifier):
    """
    Calculate number of spells known based on D&D 5e rules.
    
    For most spellcasters:
    spells_known = level + spellcasting_ability_modifier
    
    But some classes have unique mechanics:
    - Warlocks: Fixed based on level (not level + mod)
    - Sorcerers: Fixed table
    - Bard: Fixed table
    """
    class_name = class_name.lower()
    
    # Most full casters: level + spellcasting_ability_modifier
    if class_name in ['wizard', 'cleric', 'druid', 'paladin', 'ranger']:
        return level + spellcasting_ability_modifier
    
    # Warlock: Fixed progression (different system)
    elif class_name == 'warlock':
        if level <= 1: return 2
        elif level <= 2: return 3
        elif level <= 3: return 4
        elif level <= 4: return 5
        elif level <= 5: return 6
        elif level <= 6: return 7
        elif level <= 7: return 8
        elif level <= 8: return 9
        elif level <= 9: return 10
        elif level <= 10: return 11
        else: return min(11 + (level - 10), 20)
    
    # Sorcerer: Fixed table
    elif class_name == 'sorcerer':
        sorcerer_known = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10,
                         10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14,
                         17: 15, 18: 15, 19: 15, 20: 15}
        return sorcerer_known.get(level, 15)
    
    # Bard: Fixed table
    elif class_name == 'bard':
        bard_known = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12,
                     10: 13, 11: 14, 12: 15, 13: 15, 14: 15, 15: 16, 16: 16,
                     17: 17, 18: 18, 19: 18, 20: 18}
        return bard_known.get(level, 18)
    
    # Artificer: Fixed table
    elif class_name == 'artificer':
        artificer_known = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12,
                          10: 13, 11: 14, 12: 15, 13: 15, 14: 15, 15: 16, 16: 16,
                          17: 17, 18: 18, 19: 18, 20: 18}
        return artificer_known.get(level, 18)
    
    # Non-spellcasters
    return 0


# ============================================================================
# SPELL SLOT TABLES (D&D 5E)
# ============================================================================

FULL_CASTER_SLOTS = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}

HALF_CASTER_SLOTS = {
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    20: [4, 3, 3, 3, 2, 0, 0, 0, 0],
}

ARTIFICER_SLOTS = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    20: [4, 3, 3, 3, 2, 0, 0, 0, 0],
}

WARLOCK_SLOTS = {
    1: [1, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0],
    3: [0, 2, 0, 0, 0],
    4: [0, 2, 0, 0, 0],
    5: [0, 0, 2, 0, 0],
    6: [0, 0, 2, 0, 0],
    7: [0, 0, 2, 0, 0],
    8: [0, 0, 2, 0, 0],
    9: [0, 0, 2, 0, 0],
    10: [0, 0, 2, 0, 0],
    11: [0, 0, 3, 0, 0],
    12: [0, 0, 3, 0, 0],
    13: [0, 0, 3, 0, 0],
    14: [0, 0, 3, 0, 0],
    15: [0, 0, 3, 0, 0],
    16: [0, 0, 3, 0, 0],
    17: [0, 0, 0, 4, 0],
    18: [0, 0, 0, 4, 0],
    19: [0, 0, 0, 4, 0],
    20: [0, 0, 0, 4, 0],
}


def get_spell_slots(class_name, level):
    """Get spell slots for a given class and level"""
    class_name = class_name.lower()
    
    if class_name in ['wizard', 'sorcerer', 'cleric', 'druid', 'bard']:
        return FULL_CASTER_SLOTS.get(level, [0]*9)
    elif class_name in ['paladin', 'ranger']:
        return HALF_CASTER_SLOTS.get(level, [0]*9)
    elif class_name == 'artificer':
        return ARTIFICER_SLOTS.get(level, [0]*9)
    elif class_name == 'warlock':
        slots = WARLOCK_SLOTS.get(level, [0]*5)
        result = [0] * 9
        for i, count in enumerate(slots):
            if count > 0:
                result[i] = count
        return result
    else:
        return [0] * 9


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character(character, field_values):
    """Validate character sheet requirements"""
    errors = []
    
    # Check personality traits
    if not field_values.get('PersonalityTraits', '').strip():
        errors.append("FAIL: PersonalityTraits field is empty (must populate from details.personality)")
    
    # Check spellcasting if applicable
    spellcasting = character.get('spellcasting')
    if spellcasting:
        cantrips = spellcasting.get('cantrips_known', [])
        spells_known = spellcasting.get('spells_known', [])
        
        # Separate level 0 from level 1+
        cantrips_list = [s for s in spells_known if s.get('level', 0) == 0]
        leveled_spells = [s for s in spells_known if s.get('level', 0) > 0]
        
        # Validate spell count
        class_name = character['classes'][0]['name']
        level = character['classes'][0]['level']
        ability_key = spellcasting.get('ability', '').lower()
        
        ability_scores = character['ability_scores']
        if ability_key == 'intelligence':
            mod_val = ability_mod(ability_scores['int'])
        elif ability_key == 'wisdom':
            mod_val = ability_mod(ability_scores['wis'])
        elif ability_key == 'charisma':
            mod_val = ability_mod(ability_scores['cha'])
        else:
            mod_val = 0
        
        expected_spells = calculate_spells_known(class_name, level, mod_val)
        
        if len(leveled_spells) > expected_spells:
            errors.append(
                f"WARN: Too many spells known. Expected {expected_spells} "
                f"({level} + {mod_val}), got {len(leveled_spells)}. "
                f"Truncating to first {expected_spells}."
            )
    
    return errors


# ============================================================================
# PDF FIELD MAPPING (UPDATED)
# ============================================================================

def build_field_values(character):
    """
    Build complete dictionary mapping PDF field names to character values.
    CRITICAL: Handle spellcasting correctly with spell count validation.
    """
    vals = {}
    
    # Get primary class info
    primary_class = character['classes'][0]
    class_level = primary_class['level']
    pb = prof_bonus(class_level)
    
    # Ability scores
    str_score = character['ability_scores']['str']
    dex_score = character['ability_scores']['dex']
    con_score = character['ability_scores']['con']
    int_score = character['ability_scores']['int']
    wis_score = character['ability_scores']['wis']
    cha_score = character['ability_scores']['cha']
    
    # Ability modifiers
    str_mod = ability_mod(str_score)
    dex_mod = ability_mod(dex_score)
    con_mod = ability_mod(con_score)
    int_mod = ability_mod(int_score)
    wis_mod = ability_mod(wis_score)
    cha_mod = ability_mod(cha_score)
    
    # ========================================================================
    # IDENTITY & METADATA
    # ========================================================================
    vals['CharacterName'] = character['name']
    vals['CharacterName 2'] = character['name']
    vals['PlayerName'] = character['player']['name']
    vals['ClassLevel'] = f"{primary_class['name']} {class_level}"
    vals['Background'] = character['background']['name']
    vals['Race'] = character['race']['name']
    vals['Alignment'] = character['alignment']
    vals['XP'] = str(character.get('experience_points', 0))
    
    # Physical description
    phys = character.get('physical', {})
    vals['Age'] = str(phys.get('age', ''))
    vals['Height'] = phys.get('height', '')
    vals['Weight'] = phys.get('weight', '')
    vals['Eyes'] = phys.get('eyes', '')
    vals['Skin'] = phys.get('skin', '')
    vals['Hair'] = phys.get('hair', '')
    
    # ========================================================================
    # ABILITY SCORES & MODIFIERS
    # ========================================================================
    vals['STR'] = str(str_score)
    vals['DEX'] = str(dex_score)
    vals['CON'] = str(con_score)
    vals['INT'] = str(int_score)
    vals['WIS'] = str(wis_score)
    vals['CHA'] = str(cha_score)
    
    vals['STRmod'] = format_modifier(str_mod)
    vals['DEXmod '] = format_modifier(dex_mod)
    vals['CONmod'] = format_modifier(con_mod)
    vals['INTmod'] = format_modifier(int_mod)
    vals['WISmod'] = format_modifier(wis_mod)
    vals['CHamod'] = format_modifier(cha_mod)
    
    # ========================================================================
    # SAVING THROWS
    # ========================================================================
    st = character['saving_throws']
    vals['ST Strength'] = format_modifier(saving_throw_bonus(str_mod, pb, st.get('str', False)))
    vals['ST Dexterity'] = format_modifier(saving_throw_bonus(dex_mod, pb, st.get('dex', False)))
    vals['ST Constitution'] = format_modifier(saving_throw_bonus(con_mod, pb, st.get('con', False)))
    vals['ST Intelligence'] = format_modifier(saving_throw_bonus(int_mod, pb, st.get('int', False)))
    vals['ST Wisdom'] = format_modifier(saving_throw_bonus(wis_mod, pb, st.get('wis', False)))
    vals['ST Charisma'] = format_modifier(saving_throw_bonus(cha_mod, pb, st.get('cha', False)))
    
    # ========================================================================
    # SKILLS
    # ========================================================================
    skills = character['skills']
    
    skill_mapping = {
        'Acrobatics': ('Acrobatics', dex_mod),
        'Animal Handling': ('Animal', wis_mod),
        'Arcana': ('Arcana', int_mod),
        'Athletics': ('Athletics', str_mod),
        'Deception': ('Deception', cha_mod),
        'History': ('History', int_mod),
        'Insight': ('Insight', wis_mod),
        'Intimidation': ('Intimidation', cha_mod),
        'Investigation': ('Investigation', int_mod),
        'Medicine': ('Medicine', wis_mod),
        'Nature': ('Nature', int_mod),
        'Perception': ('Perception', wis_mod),
        'Performance': ('Performance', cha_mod),
        'Persuasion': ('Persuasion', cha_mod),
        'Religion': ('Religion', int_mod),
        'Sleight of Hand': ('SleightofHand', dex_mod),
        'Stealth': ('Stealth', dex_mod),
        'Survival': ('Survival', wis_mod),
    }
    
    for skill_name, (pdf_field, ability) in skill_mapping.items():
        is_proficient = skills.get(skill_name, False)
        bonus = skill_bonus(ability, pb, is_proficient)
        vals[pdf_field] = format_modifier(bonus)
    
    # ========================================================================
    # COMBAT STATS
    # ========================================================================
    vals['AC'] = str(character['armor_class']['value'])
    vals['Initiative'] = format_modifier(character.get('initiative_bonus', dex_mod))
    vals['Speed'] = str(character['speed'].get('Walk', 30))
    
    hp = character['hit_points']
    vals['HPMax'] = str(hp['max'])
    vals['HPCurrent'] = str(hp['current'])
    vals['HPTemp'] = str(hp.get('temp', 0))
    
    hd = character['hit_dice']
    vals['HDTotal'] = hd['total']
    vals['HD'] = str(hd['current'])
    
    vals['Inspiration'] = '1' if character.get('inspiration', False) else '0'
    vals['ProfBonus'] = format_modifier(pb)
    
    perception_skill = skills.get('Perception', False)
    perception_bonus = skill_bonus(wis_mod, pb, perception_skill)
    vals['Passive'] = str(passive_perception(perception_bonus))
    
    # ========================================================================
    # CURRENCY
    # ========================================================================
    currency = character.get('currency', {})
    vals['CP'] = str(currency.get('cp', 0))
    vals['SP'] = str(currency.get('sp', 0))
    vals['EP'] = str(currency.get('ep', 0))
    vals['GP'] = str(currency.get('gp', 0))
    vals['PP'] = str(currency.get('pp', 0))
    
    # ========================================================================
    # WEAPONS
    # ========================================================================
    weapons = character.get('weapons', [])
    
    if len(weapons) > 0:
        w = weapons[0]
        vals['Wpn Name'] = w['name']
        vals['Wpn1 AtkBonus'] = format_modifier(w['attack_bonus'])
        vals['Wpn1 Damage'] = f"{w['damage']} {w['damage_type']}"
    
    if len(weapons) > 1:
        w = weapons[1]
        vals['Wpn Name 2'] = w['name']
        vals['Wpn2 AtkBonus'] = format_modifier(w['attack_bonus'])
        vals['Wpn2 Damage'] = f"{w['damage']} {w['damage_type']}"
    
    if len(weapons) > 2:
        w = weapons[2]
        vals['Wpn Name 3'] = w['name']
        vals['Wpn3 AtkBonus'] = format_modifier(w['attack_bonus'])
        vals['Wpn3 Damage'] = f"{w['damage']} {w['damage_type']}"
    
    vals['AttacksSpellcasting'] = character.get('attacks_and_spellcasting', '')
    
    # ========================================================================
    # PERSONALITY & ROLEPLAY (BUG FIX: EXPLICIT MAPPING)
    # ========================================================================
    details = character['details']
    # CRITICAL: Map personality ONLY to PersonalityTraits
    vals['PersonalityTraits'] = details['personality']
    vals['Ideals'] = details['ideal']
    vals['Bonds'] = details['bond']
    vals['Flaws'] = details['flaw']
    
    vals['Backstory'] = character.get('backstory', '')
    vals['Allies'] = character.get('allies_and_organizations', '')
    vals['Treasure'] = character.get('treasure', '')
    
    faction = character.get('faction', {})
    vals['FactionName'] = faction.get('name', '')
    
    # ========================================================================
    # PROFICIENCIES & LANGUAGES
    # ========================================================================
    languages = character.get('languages', [])
    proficiencies = character.get('proficiencies', [])
    
    prof_text = "Languages: " + ", ".join(languages)
    if proficiencies:
        prof_text += "\n\nProficiencies: " + ", ".join(proficiencies)
    
    vals['ProficienciesLang'] = prof_text
    
    # ========================================================================
    # FEATURES & TRAITS
    # ========================================================================
    features = character.get('features_and_traits', [])
    feats = character.get('feats', [])
    
    features_text = "\n\n".join(features)
    if feats:
        features_text += "\n\nFeats:\n" + "\n".join(feats)
    
    vals['Feat+Traits'] = features_text
    vals['Features and Traits'] = features_text
    
    # ========================================================================
    # EQUIPMENT
    # ========================================================================
    equipment = character.get('equipment', [])
    if equipment:
        vals['Equipment'] = "\n".join(equipment)
    
    # ========================================================================
    # SPELLCASTING (CRITICAL FIXES)
    # ========================================================================
    spellcasting = character.get('spellcasting')
    
    if spellcasting:
        vals['Spellcasting Class 2'] = spellcasting['class']
        vals['SpellcastingAbility 2'] = spellcasting['ability'].upper()
        vals['SpellSaveDC  2'] = str(spellcasting['spell_save_dc'])
        vals['SpellAtkBonus 2'] = format_modifier(spellcasting['spell_attack_bonus'])
        
        # Spell slots
        spell_slots = spellcasting.get('spell_slots', {})
        
        for level in range(1, 10):
            slot_key = f'level_{level}'
            if slot_key in spell_slots:
                vals[f'SlotsTotal {18+level}'] = str(spell_slots[slot_key]['total'])
                vals[f'SlotsRemaining {18+level}'] = str(spell_slots[slot_key]['remaining'])
        
        # ====================================================================
        # SPELLS (CRITICAL FIX: Separate cantrips from leveled spells)
        # ====================================================================
        spells_list = spellcasting.get('spells_known', [])
        
        # Separate level 0 (cantrips) from leveled spells
        cantrips_list = [s for s in spells_list if s.get('level', 0) == 0]
        leveled_spells = [s for s in spells_list if s.get('level', 0) > 0]
        
        # TRUNCATE leveled spells to allowed count
        class_name = primary_class['name']
        spellcasting_ability = spellcasting.get('ability', '').lower()
        
        if spellcasting_ability == 'intelligence':
            ability_mod_val = int_mod
        elif spellcasting_ability == 'wisdom':
            ability_mod_val = wis_mod
        elif spellcasting_ability == 'charisma':
            ability_mod_val = cha_mod
        else:
            ability_mod_val = 0
        
        max_spells = calculate_spells_known(class_name, class_level, ability_mod_val)
        if len(leveled_spells) > max_spells:
            leveled_spells = leveled_spells[:max_spells]
        
        # Build all spells list: cantrips first, then leveled
        all_spells = []
        
        # Format cantrips
        for cantrip in cantrips_list:
            name = cantrip.get('name', '')
            all_spells.append(f"{name} (Cantrip)")
        
        # Format leveled spells
        for spell in leveled_spells:
            spell_name = spell['name']
            spell_level = spell['level']
            prepared = spell.get('prepared', False)
            ritual = spell.get('ritual', False)
            
            suffix = f" ({spell_level})"
            if prepared:
                suffix += " [P]"
            if ritual:
                suffix += " [R]"
            
            all_spells.append(spell_name + suffix)
        
        # Fill spell fields
        spell_fields = (
            [f"Spells 1010{i}" for i in range(10)] +
            [f"Spells {1014 + i}" for i in range(86)] +
            [f"Spells 10101{i}" for i in range(4)]
        )
        
        for i, spell_name in enumerate(all_spells):
            if i < len(spell_fields):
                vals[spell_fields[i]] = spell_name
    
    return vals


# ============================================================================
# MAIN CLI FUNCTION
# ============================================================================

def generate_character_sheet(character_json_path, output_folder="generated_character_sheets"):
    """
    Main function to generate and fill a character sheet PDF.
    
    Usage:
        python fill_character_sheet_complete.py --character path/to/character.json
        
        OR call this function directly:
        from fill_character_sheet_complete import generate_character_sheet
        generate_character_sheet("examples/Character.level3.json")
    """
    
    # Load character
    print(f"📖 Loading character from {character_json_path}...")
    with open(character_json_path, 'r', encoding='utf-8') as f:
        character = json.load(f)
    
    # Setup output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    char_name = character['name'].replace(" ", "")
    level = character['classes'][0]['level']
    output_filename = f"{char_name}_Level{level}.pdf"
    output_file = output_path / output_filename
    
    # Load PDF template
    pdf_template = "assets/5E_CharacterSheet_Fillable.pdf"
    print(f"📄 Loading PDF template from {pdf_template}...")
    reader = PdfReader(pdf_template)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    
    # Build field values
    print("🧮 Calculating D&D 5e stats and building field mappings...")
    field_values = build_field_values(character)
    
    # VALIDATE
    print("✓ Validating character sheet requirements...")
    validation_errors = validate_character(character, field_values)
    
    if validation_errors:
        for error in validation_errors:
            if error.startswith("FAIL"):
                print(f"❌ {error}")
                sys.exit(1)
            else:
                print(f"⚠️  {error}")
    
    # Fill PDF
    print(f"✏️  Filling {len(field_values)} PDF fields...")
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)
    
    # Ensure fields are visible
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)}
        )
    
    # Write output
    print(f"💾 Writing filled PDF to {output_file}...")
    with open(output_file, "wb") as f:
        writer.write(f)
    
    print()
    print("=" * 60)
    print("✅ SUCCESS! Character sheet generated!")
    print("=" * 60)
    print(f"📋 Character: {character['name']}")
    print(f"🎯 Class: {character['classes'][0]['name']} {level}")
    print(f"📊 Fields filled: {len(field_values)}")
    print(f"📁 Output: {output_file}")
    print("=" * 60)
    print()
    
    return str(output_file)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    ap = argparse.ArgumentParser(
        description='Generate D&D 5e character sheet PDFs with full field coverage'
    )
    ap.add_argument("--character", required=True, help="Path to character JSON file")
    ap.add_argument("--out-folder", default="generated_character_sheets", 
                    help="Output folder for generated PDFs")
    args = ap.parse_args()
    
    generate_character_sheet(args.character, args.out_folder)


if __name__ == "__main__":
    main()
