"""
D&D 5e Character Sheet PDF Filler - Complete MVP
Fills all available fields in the official D&D 5e character sheet PDF
"""

import json
import argparse
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
# SPELL SLOT TABLES (D&D 5E)
# ============================================================================

# Spell slots by class level for full casters (Wizard, Cleric, Druid, etc.)
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

# Half casters (Paladin, Ranger) - spell slots
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

# Artificer (also half caster but different progression)
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

# Warlock uses pact magic (different system)
WARLOCK_SLOTS = {
    1: [1, 0, 0, 0, 0],  # [slots, slot_level, 0, 0, 0]
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
    
    # Full casters
    if class_name in ['wizard', 'sorcerer', 'cleric', 'druid', 'bard']:
        return FULL_CASTER_SLOTS.get(level, [0]*9)
    
    # Half casters
    elif class_name in ['paladin', 'ranger']:
        return HALF_CASTER_SLOTS.get(level, [0]*9)
    
    # Artificer
    elif class_name == 'artificer':
        return ARTIFICER_SLOTS.get(level, [0]*9)
    
    # Warlock (special case)
    elif class_name == 'warlock':
        slots = WARLOCK_SLOTS.get(level, [0]*5)
        # Convert warlock's pact magic to standard format
        result = [0] * 9
        for i, count in enumerate(slots):
            if count > 0:
                result[i] = count
        return result
    
    # Non-spellcaster
    else:
        return [0] * 9


# ============================================================================
# PDF FIELD MAPPING
# ============================================================================

def build_field_values(character):
    """
    Build complete dictionary mapping PDF field names to character values.
    Implements all D&D 5e calculations.
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
    vals['CharacterName 2'] = character['name']  # Second page
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
    
    # Map JSON skill names to PDF field names and ability scores
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
    
    # Passive Perception
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
    
    # Additional attacks/spellcasting notes
    vals['AttacksSpellcasting'] = character.get('attacks_and_spellcasting', '')
    
    # ========================================================================
    # PERSONALITY & ROLEPLAY
    # ========================================================================
    details = character['details']
    vals['PersonalityTraits'] = details['personality']
    vals['Ideals'] = details['ideal']
    vals['Bonds'] = details['bond']
    vals['Flaws'] = details['flaw']
    
    vals['Backstory'] = character.get('backstory', '')
    vals['Allies'] = character.get('allies_and_organizations', '')
    vals['Treasure'] = character.get('treasure', '')
    
    # Faction
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
    vals['Features and Traits'] = features_text  # Also fill the other field
    
    # ========================================================================
    # EQUIPMENT
    # ========================================================================
    equipment = character.get('equipment', [])
    if equipment:
        vals['Equipment'] = "\n".join(equipment)
    
    # ========================================================================
    # SPELLCASTING
    # ========================================================================
    spellcasting = character.get('spellcasting')
    
    if spellcasting:
        vals['Spellcasting Class 2'] = spellcasting['class']
        vals['SpellcastingAbility 2'] = spellcasting['ability'].upper()
        vals['SpellSaveDC  2'] = str(spellcasting['spell_save_dc'])
        vals['SpellAtkBonus 2'] = format_modifier(spellcasting['spell_attack_bonus'])
        
        # Spell slots
        spell_slots = spellcasting.get('spell_slots', {})
        
        # Level 1 slots (fields 19)
        if 'level_1' in spell_slots:
            vals['SlotsTotal 19'] = str(spell_slots['level_1']['total'])
            vals['SlotsRemaining 19'] = str(spell_slots['level_1']['remaining'])
        
        # Level 2 slots (fields 20)
        if 'level_2' in spell_slots:
            vals['SlotsTotal 20'] = str(spell_slots['level_2']['total'])
            vals['SlotsRemaining 20'] = str(spell_slots['level_2']['remaining'])
        
        # Level 3 slots (fields 21)
        if 'level_3' in spell_slots:
            vals['SlotsTotal 21'] = str(spell_slots['level_3']['total'])
            vals['SlotsRemaining 21'] = str(spell_slots['level_3']['remaining'])
        
        # Level 4 slots (fields 22)
        if 'level_4' in spell_slots:
            vals['SlotsTotal 22'] = str(spell_slots['level_4']['total'])
            vals['SlotsRemaining 22'] = str(spell_slots['level_4']['remaining'])
        
        # Level 5 slots (fields 23)
        if 'level_5' in spell_slots:
            vals['SlotsTotal 23'] = str(spell_slots['level_5']['total'])
            vals['SlotsRemaining 23'] = str(spell_slots['level_5']['remaining'])
        
        # Level 6 slots (fields 24)
        if 'level_6' in spell_slots:
            vals['SlotsTotal 24'] = str(spell_slots['level_6']['total'])
            vals['SlotsRemaining 24'] = str(spell_slots['level_6']['remaining'])
        
        # Level 7 slots (fields 25)
        if 'level_7' in spell_slots:
            vals['SlotsTotal 25'] = str(spell_slots['level_7']['total'])
            vals['SlotsRemaining 25'] = str(spell_slots['level_7']['remaining'])
        
        # Level 8 slots (fields 26)
        if 'level_8' in spell_slots:
            vals['SlotsTotal 26'] = str(spell_slots['level_8']['total'])
            vals['SlotsRemaining 26'] = str(spell_slots['level_8']['remaining'])
        
        # Level 9 slots (fields 27)
        if 'level_9' in spell_slots:
            vals['SlotsTotal 27'] = str(spell_slots['level_9']['total'])
            vals['SlotsRemaining 27'] = str(spell_slots['level_9']['remaining'])
        
        # Spell names - build list of all spells (cantrips + leveled)
        all_spells = []
        
        # Add cantrips first
        if 'cantrips_known' in spellcasting:
            for cantrip in spellcasting['cantrips_known']:
                all_spells.append(f"{cantrip} (Cantrip)")
        
        # Add leveled spells
        if 'spells_known' in spellcasting:
            for spell in spellcasting['spells_known']:
                spell_name = spell['name']
                spell_level = spell['level']
                prepared = spell.get('prepared', False)
                ritual = spell.get('ritual', False)
                
                # Format: "Fireball (3)" or "Fireball (3) [P]" if prepared
                suffix = f" ({spell_level})"
                if prepared:
                    suffix += " [P]"
                if ritual:
                    suffix += " [R]"
                
                all_spells.append(spell_name + suffix)
        
        # Fill spell name fields (Spells 10100 through Spells 1099)
        # The fields go: 10100-10109, 1014-1099, 101010-101013
        spell_fields = (
            [f"Spells 1010{i}" for i in range(10)] +  # 10100-10109
            [f"Spells {1014 + i}" for i in range(86)] +  # 1014-1099
            [f"Spells 10101{i}" for i in range(4)]  # 101010-101013
        )
        
        for i, spell_name in enumerate(all_spells):
            if i < len(spell_fields):
                vals[spell_fields[i]] = spell_name
    
    return vals


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    ap = argparse.ArgumentParser(
        description='Fill D&D 5e character sheet PDF with complete field coverage'
    )
    ap.add_argument("--pdf", required=True, help="Path to blank character sheet PDF")
    ap.add_argument("--character", required=True, help="Path to character JSON file")
    ap.add_argument("--out", default="filled_character.pdf", help="Output PDF filename")
    args = ap.parse_args()
    
    # Load character data
    print(f"Loading character from {args.character}...")
    with open(args.character, 'r', encoding='utf-8') as f:
        character = json.load(f)
    
    # Load PDF
    print(f"Loading PDF from {args.pdf}...")
    reader = PdfReader(args.pdf)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    
    # Build field values
    print("Calculating D&D 5e stats and building field mappings...")
    field_values = build_field_values(character)
    
    print(f"Filling {len(field_values)} fields...")
    
    # Update all pages with field values
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)
    
    # Ensure fields are visible (required for some PDF viewers)
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)}
        )
    
    # Write output
    print(f"Writing filled PDF to {args.out}...")
    with open(args.out, "wb") as f:
        writer.write(f)
    
    print("✓ Complete! Character sheet filled successfully.")
    print(f"  Character: {character['name']}")
    print(f"  Class: {character['classes'][0]['name']} {character['classes'][0]['level']}")
    print(f"  Fields filled: {len(field_values)}")


if __name__ == "__main__":
    main()
