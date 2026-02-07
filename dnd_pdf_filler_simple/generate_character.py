"""
D&D 5e Character Sheet PDF Filler
Fills all available fields in the official D&D 5e character sheet PDF
using the exact AcroForm field IDs.
"""

import json
import argparse
import os
import shutil
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


def skill_bonus(ability_mod_val, prof_bonus_val, is_proficient):
    """Calculate skill bonus"""
    return ability_mod_val + (prof_bonus_val if is_proficient else 0)


def saving_throw_bonus(ability_mod_val, prof_bonus_val, is_proficient):
    """Calculate saving throw bonus"""
    return ability_mod_val + (prof_bonus_val if is_proficient else 0)


def passive_perception(perception_bonus):
    """Calculate passive perception"""
    return 10 + perception_bonus


def format_modifier(value):
    """Format modifier with + or - sign"""
    return f"+{value}" if value >= 0 else str(value)


# ============================================================================
# NON-NEGOTIABLE PDF FIELD MAPPINGS
# ============================================================================

# Saving throw proficiency checkboxes (page 1)
CHECKBOX_TO_PROF_FIELD = {
    # Saving throw proficiency
    "Check Box 11": "ST Strength",
    "Check Box 18": "ST Dexterity",
    "Check Box 19": "ST Constitution",
    "Check Box 20": "ST Intelligence",
    "Check Box 21": "ST Wisdom",
    "Check Box 22": "ST Charisma",

    # Skill proficiency (top to bottom)
    "Check Box 23": "Acrobatics",
    "Check Box 24": "Animal Handling",
    "Check Box 25": "Arcana",
    "Check Box 26": "Athletics",
    "Check Box 27": "Deception",
    "Check Box 28": "History",
    "Check Box 29": "Insight",
    "Check Box 30": "Intimidation",
    "Check Box 31": "Investigation",
    "Check Box 32": "Medicine",
    "Check Box 33": "Nature",
    "Check Box 34": "Perception",
    "Check Box 35": "Performance",
    "Check Box 36": "Persuasion",
    "Check Box 37": "Religion",
    "Check Box 38": "Sleight of Hand",
    "Check Box 39": "Stealth",
    "Check Box 40": "Survival",
}

# Death save checkboxes (page 1)
DEATH_SAVE_CHECKBOXES = {
    "success": ["Check Box 12", "Check Box 13", "Check Box 14"],
    "failure": ["Check Box 15", "Check Box 16", "Check Box 17"],
}

# Cantrip fields (level 0) - NO prepared checkboxes
CANTRIP_FIELDS = [
    "Spells 1014",
    "Spells 1016",
    "Spells 1017",
    "Spells 1018",
    "Spells 1019",
    "Spells 1020",
    "Spells 1021",
    "Spells 1022",
]

# Spell name fields by level (1-9)
SPELL_FIELDS_BY_LEVEL = {
    1: [
        "Spells 1015", "Spells 1023", "Spells 1024", "Spells 1025",
        "Spells 1026", "Spells 1027", "Spells 1028", "Spells 1029",
        "Spells 1030", "Spells 1031", "Spells 1032", "Spells 1033",
    ],
    2: [
        "Spells 1046", "Spells 1034", "Spells 1035", "Spells 1036",
        "Spells 1037", "Spells 1038", "Spells 1039", "Spells 1040",
        "Spells 1041", "Spells 1042", "Spells 1043", "Spells 1044",
        "Spells 1045",
    ],
    3: [
        "Spells 1048", "Spells 1047", "Spells 1049", "Spells 1050",
        "Spells 1051", "Spells 1052", "Spells 1053", "Spells 1054",
        "Spells 1055", "Spells 1056", "Spells 1057", "Spells 1058",
        "Spells 1059",
    ],
    4: [
        "Spells 1061", "Spells 1060", "Spells 1062", "Spells 1063",
        "Spells 1064", "Spells 1065", "Spells 1066", "Spells 1067",
        "Spells 1068", "Spells 1069", "Spells 1070", "Spells 1071",
        "Spells 1072",
    ],
    5: [
        "Spells 1074", "Spells 1073", "Spells 1075", "Spells 1076",
        "Spells 1077", "Spells 1078", "Spells 1079", "Spells 1080",
        "Spells 1081",
    ],
    6: [
        "Spells 1083", "Spells 1082", "Spells 1084", "Spells 1085",
        "Spells 1086", "Spells 1087", "Spells 1088", "Spells 1089",
        "Spells 1090",
    ],
    7: [
        "Spells 1092", "Spells 1091", "Spells 1093", "Spells 1094",
        "Spells 1095", "Spells 1096", "Spells 1097", "Spells 1098",
        "Spells 1099",
    ],
    8: [
        "Spells 10101", "Spells 10100", "Spells 10102", "Spells 10103",
        "Spells 10104", "Spells 10105", "Spells 10106",
    ],
    9: [
        "Spells 10108", "Spells 10107", "Spells 10109", "Spells 101010",
        "Spells 101011", "Spells 101012", "Spells 101013",
    ],
}

# Spell name field -> prepared checkbox field mapping
SPELL_FIELD_TO_PREP_CHECKBOX = {
    # Level 1 lines
    "Spells 1015":  "Check Box 251",
    "Spells 1023":  "Check Box 309",
    "Spells 1024":  "Check Box 3010",
    "Spells 1025":  "Check Box 3011",
    "Spells 1026":  "Check Box 3012",
    "Spells 1027":  "Check Box 3013",
    "Spells 1028":  "Check Box 3014",
    "Spells 1029":  "Check Box 3015",
    "Spells 1030":  "Check Box 3016",
    "Spells 1031":  "Check Box 3017",
    "Spells 1032":  "Check Box 3018",
    "Spells 1033":  "Check Box 3019",

    # Level 2 lines
    "Spells 1046":  "Check Box 313",
    "Spells 1034":  "Check Box 310",
    "Spells 1035":  "Check Box 3020",
    "Spells 1036":  "Check Box 3021",
    "Spells 1037":  "Check Box 3022",
    "Spells 1038":  "Check Box 3023",
    "Spells 1039":  "Check Box 3024",
    "Spells 1040":  "Check Box 3025",
    "Spells 1041":  "Check Box 3026",
    "Spells 1042":  "Check Box 3027",
    "Spells 1043":  "Check Box 3028",
    "Spells 1044":  "Check Box 3029",
    "Spells 1045":  "Check Box 3030",

    # Level 3 lines
    "Spells 1048":  "Check Box 315",
    "Spells 1047":  "Check Box 314",
    "Spells 1049":  "Check Box 3031",
    "Spells 1050":  "Check Box 3032",
    "Spells 1051":  "Check Box 3033",
    "Spells 1052":  "Check Box 3034",
    "Spells 1053":  "Check Box 3035",
    "Spells 1054":  "Check Box 3036",
    "Spells 1055":  "Check Box 3037",
    "Spells 1056":  "Check Box 3038",
    "Spells 1057":  "Check Box 3039",
    "Spells 1058":  "Check Box 3040",
    "Spells 1059":  "Check Box 3041",

    # Level 4 lines
    "Spells 1061":  "Check Box 317",
    "Spells 1060":  "Check Box 316",
    "Spells 1062":  "Check Box 3042",
    "Spells 1063":  "Check Box 3043",
    "Spells 1064":  "Check Box 3044",
    "Spells 1065":  "Check Box 3045",
    "Spells 1066":  "Check Box 3046",
    "Spells 1067":  "Check Box 3047",
    "Spells 1068":  "Check Box 3048",
    "Spells 1069":  "Check Box 3049",
    "Spells 1070":  "Check Box 3050",
    "Spells 1071":  "Check Box 3051",
    "Spells 1072":  "Check Box 3052",

    # Level 5 lines
    "Spells 1074":  "Check Box 319",
    "Spells 1073":  "Check Box 318",
    "Spells 1075":  "Check Box 3053",
    "Spells 1076":  "Check Box 3054",
    "Spells 1077":  "Check Box 3055",
    "Spells 1078":  "Check Box 3056",
    "Spells 1079":  "Check Box 3057",
    "Spells 1080":  "Check Box 3058",
    "Spells 1081":  "Check Box 3059",

    # Level 6 lines
    "Spells 1083":  "Check Box 321",
    "Spells 1082":  "Check Box 320",
    "Spells 1084":  "Check Box 3060",
    "Spells 1085":  "Check Box 3061",
    "Spells 1086":  "Check Box 3062",
    "Spells 1087":  "Check Box 3063",
    "Spells 1088":  "Check Box 3064",
    "Spells 1089":  "Check Box 3065",
    "Spells 1090":  "Check Box 3066",

    # Level 7 lines
    "Spells 1092":  "Check Box 323",
    "Spells 1091":  "Check Box 322",
    "Spells 1093":  "Check Box 3067",
    "Spells 1094":  "Check Box 3068",
    "Spells 1095":  "Check Box 3069",
    "Spells 1096":  "Check Box 3070",
    "Spells 1097":  "Check Box 3071",
    "Spells 1098":  "Check Box 3072",
    "Spells 1099":  "Check Box 3073",

    # Level 8 lines
    "Spells 10101": "Check Box 325",
    "Spells 10100": "Check Box 324",
    "Spells 10102": "Check Box 3074",
    "Spells 10103": "Check Box 3075",
    "Spells 10104": "Check Box 3076",
    "Spells 10105": "Check Box 3077",
    "Spells 10106": "Check Box 3078",

    # Level 9 lines
    "Spells 10108": "Check Box 327",
    "Spells 10107": "Check Box 326",
    "Spells 10109": "Check Box 3079",
    "Spells 101010": "Check Box 3080",
    "Spells 101011": "Check Box 3081",
    "Spells 101012": "Check Box 3082",
    "Spells 101013": "Check Box 3083",
}

# Skill name -> (PDF text field name, ability key)
# Note: Some PDF field names have trailing spaces
SKILL_MAP = {
    "Acrobatics":      ("Acrobatics",       "dex"),
    "Animal Handling": ("Animal",           "wis"),
    "Arcana":          ("Arcana",           "int"),
    "Athletics":       ("Athletics",        "str"),
    "Deception":       ("Deception ",       "cha"),   # trailing space
    "History":         ("History ",         "int"),   # trailing space
    "Insight":         ("Insight",          "wis"),
    "Intimidation":    ("Intimidation",     "cha"),
    "Investigation":   ("Investigation ",   "int"),   # trailing space
    "Medicine":        ("Medicine",         "wis"),
    "Nature":          ("Nature",           "int"),
    "Perception":      ("Perception ",      "wis"),   # trailing space
    "Performance":     ("Performance",      "cha"),
    "Persuasion":      ("Persuasion",       "cha"),
    "Religion":        ("Religion",         "int"),
    "Sleight of Hand": ("SleightofHand",    "dex"),
    "Stealth":         ("Stealth ",         "dex"),   # trailing space
    "Survival":        ("Survival",         "wis"),
}

# Saving throw checkbox -> ability key
ST_CHECKBOX_TO_ABILITY = {
    "Check Box 11": "str",
    "Check Box 18": "dex",
    "Check Box 19": "con",
    "Check Box 20": "int",
    "Check Box 21": "wis",
    "Check Box 22": "cha",
}

# Skill checkbox -> skill name
SKILL_CHECKBOX_TO_SKILL = {
    "Check Box 23": "Acrobatics",
    "Check Box 24": "Animal Handling",
    "Check Box 25": "Arcana",
    "Check Box 26": "Athletics",
    "Check Box 27": "Deception",
    "Check Box 28": "History",
    "Check Box 29": "Insight",
    "Check Box 30": "Intimidation",
    "Check Box 31": "Investigation",
    "Check Box 32": "Medicine",
    "Check Box 33": "Nature",
    "Check Box 34": "Perception",
    "Check Box 35": "Performance",
    "Check Box 36": "Persuasion",
    "Check Box 37": "Religion",
    "Check Box 38": "Sleight of Hand",
    "Check Box 39": "Stealth",
    "Check Box 40": "Survival",
}

# "Known spells" casters - treat all known spells as prepared for MVP
KNOWN_SPELLS_CASTERS = ["sorcerer", "bard", "warlock", "ranger"]


# ============================================================================
# SPELL SLOT TABLES (D&D 5E)
# ============================================================================

FULL_CASTER_SLOTS = {
    1:  [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2:  [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3:  [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4:  [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5:  [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6:  [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7:  [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8:  [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9:  [4, 3, 3, 3, 1, 0, 0, 0, 0],
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
    1:  [0, 0, 0, 0, 0, 0, 0, 0, 0],
    2:  [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3:  [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4:  [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5:  [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6:  [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7:  [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8:  [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9:  [4, 3, 2, 0, 0, 0, 0, 0, 0],
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


def get_spell_slots(class_name, level):
    """Get spell slots for a given class and level"""
    class_name = class_name.lower()
    if class_name in ['wizard', 'sorcerer', 'cleric', 'druid', 'bard']:
        return FULL_CASTER_SLOTS.get(level, [0]*9)
    elif class_name in ['paladin', 'ranger']:
        return HALF_CASTER_SLOTS.get(level, [0]*9)
    else:
        return [0] * 9


# ============================================================================
# CHECKBOX HELPER
# ============================================================================

def set_checkboxes(writer, checkbox_vals):
    """
    Toggle checkbox annotations directly in the page tree.
    checkbox_vals: {field_name: bool}
    
    In this PDF:
    - "on" value = "Yes"
    - "off" value = "Off"
    """
    for page in writer.pages:
        if "/Annots" not in page:
            continue
        for annot_ref in page["/Annots"]:
            annot = annot_ref.get_object()
            field_name = annot.get("/T")
            if field_name is None:
                continue
            field_name = str(field_name)
            if field_name in checkbox_vals:
                if checkbox_vals[field_name]:
                    annot.update({
                        NameObject("/V"):  NameObject("/Yes"),
                        NameObject("/AS"): NameObject("/Yes"),
                    })
                else:
                    annot.update({
                        NameObject("/V"):  NameObject("/Off"),
                        NameObject("/AS"): NameObject("/Off"),
                    })


# ============================================================================
# BUILD FIELD VALUES
# ============================================================================

def build_field_values(character):
    """
    Build complete dictionary mapping PDF field names to character values.
    Returns (text_vals, checkbox_vals)
    """
    vals = {}
    cb = {}  # checkbox values: {field_name: bool}
    
    # Get primary class info
    primary_class = character['classes'][0]
    class_level = primary_class['level']
    class_name = primary_class['name']
    pb = prof_bonus(class_level)
    
    # Ability scores
    scores = character['ability_scores']
    str_score = scores['str']
    dex_score = scores['dex']
    con_score = scores['con']
    int_score = scores['int']
    wis_score = scores['wis']
    cha_score = scores['cha']
    
    # Ability modifiers
    str_mod = ability_mod(str_score)
    dex_mod = ability_mod(dex_score)
    con_mod = ability_mod(con_score)
    int_mod = ability_mod(int_score)
    wis_mod = ability_mod(wis_score)
    cha_mod = ability_mod(cha_score)
    
    mods = {
        "str": str_mod, "dex": dex_mod, "con": con_mod,
        "int": int_mod, "wis": wis_mod, "cha": cha_mod
    }
    
    # ========================================================================
    # IDENTITY & METADATA
    # ========================================================================
    vals['CharacterName'] = character['name']
    vals['CharacterName 2'] = character['name']  # Page 2/3
    vals['PlayerName'] = character.get('player', {}).get('name', '')
    vals['ClassLevel'] = f"{class_name} {class_level}"
    vals['Background'] = character.get('background', {}).get('name', '')
    vals['Race '] = character.get('race', {}).get('name', '')  # trailing space!
    vals['Alignment'] = character.get('alignment', '')
    vals['XP'] = str(character.get('experience_points', 0))
    
    # Physical description (page 2)
    phys = character.get('physical', {})
    vals['Age'] = str(phys.get('age', ''))
    vals['Height'] = str(phys.get('height', ''))
    vals['Weight'] = str(phys.get('weight', ''))
    vals['Eyes'] = str(phys.get('eyes', ''))
    vals['Skin'] = str(phys.get('skin', ''))
    vals['Hair'] = str(phys.get('hair', ''))
    
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
    vals['DEXmod '] = format_modifier(dex_mod)  # trailing space!
    vals['CONmod'] = format_modifier(con_mod)
    vals['INTmod'] = format_modifier(int_mod)
    vals['WISmod'] = format_modifier(wis_mod)
    vals['CHamod'] = format_modifier(cha_mod)  # PDF typo: "CHa" not "CHA"
    
    # ========================================================================
    # PROFICIENCY BONUS & INSPIRATION
    # ========================================================================
    vals['ProfBonus'] = format_modifier(pb)
    vals['Inspiration'] = '1' if character.get('inspiration', False) else ''
    
    # ========================================================================
    # SAVING THROWS (text values + checkboxes)
    # ========================================================================
    st = character.get('saving_throws', {})
    
    # Text fields
    vals['ST Strength'] = format_modifier(saving_throw_bonus(str_mod, pb, st.get('str', False)))
    vals['ST Dexterity'] = format_modifier(saving_throw_bonus(dex_mod, pb, st.get('dex', False)))
    vals['ST Constitution'] = format_modifier(saving_throw_bonus(con_mod, pb, st.get('con', False)))
    vals['ST Intelligence'] = format_modifier(saving_throw_bonus(int_mod, pb, st.get('int', False)))
    vals['ST Wisdom'] = format_modifier(saving_throw_bonus(wis_mod, pb, st.get('wis', False)))
    vals['ST Charisma'] = format_modifier(saving_throw_bonus(cha_mod, pb, st.get('cha', False)))
    
    # Checkboxes
    for checkbox_name, ability_key in ST_CHECKBOX_TO_ABILITY.items():
        cb[checkbox_name] = st.get(ability_key, False)
    
    # ========================================================================
    # SKILLS (text values + checkboxes)
    # ========================================================================
    skills = character.get('skills', {})
    
    for skill_name, (pdf_field, ability_key) in SKILL_MAP.items():
        is_proficient = skills.get(skill_name, False)
        bonus = skill_bonus(mods[ability_key], pb, is_proficient)
        vals[pdf_field] = format_modifier(bonus)
    
    # Skill proficiency checkboxes
    for checkbox_name, skill_name in SKILL_CHECKBOX_TO_SKILL.items():
        cb[checkbox_name] = skills.get(skill_name, False)
    
    # Passive Perception
    perception_prof = skills.get('Perception', False)
    perception_bonus = skill_bonus(wis_mod, pb, perception_prof)
    vals['Passive'] = str(passive_perception(perception_bonus))
    
    # ========================================================================
    # COMBAT STATS
    # ========================================================================
    vals['AC'] = str(character.get('armor_class', {}).get('value', 10))
    vals['Initiative'] = format_modifier(character.get('initiative_bonus', dex_mod))
    vals['Speed'] = str(character.get('speed', {}).get('Walk', 30))
    
    hp = character.get('hit_points', {})
    vals['HPMax'] = str(hp.get('max', 0))
    vals['HPCurrent'] = str(hp.get('current', hp.get('max', 0)))
    vals['HPTemp'] = str(hp.get('temp', 0))
    
    hd = character.get('hit_dice', {})
    vals['HDTotal'] = str(hd.get('total', ''))
    vals['HD'] = str(hd.get('current', ''))
    
    # ========================================================================
    # DEATH SAVES (checkboxes)
    # ========================================================================
    ds = character.get('death_saves', {})
    successes = ds.get('successes', 0)
    failures = ds.get('failures', 0)
    
    for i, checkbox_name in enumerate(DEATH_SAVE_CHECKBOXES['success']):
        cb[checkbox_name] = (i < successes)
    for i, checkbox_name in enumerate(DEATH_SAVE_CHECKBOXES['failure']):
        cb[checkbox_name] = (i < failures)
    
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
        vals['Wpn2 AtkBonus '] = format_modifier(w['attack_bonus'])  # trailing space
        vals['Wpn2 Damage '] = f"{w['damage']} {w['damage_type']}"   # trailing space
    
    if len(weapons) > 2:
        w = weapons[2]
        vals['Wpn Name 3'] = w['name']
        vals['Wpn3 AtkBonus  '] = format_modifier(w['attack_bonus'])  # two trailing spaces
        vals['Wpn3 Damage '] = f"{w['damage']} {w['damage_type']}"    # trailing space
    
    vals['AttacksSpellcasting'] = character.get('attacks_and_spellcasting', '')
    
    # ========================================================================
    # PERSONALITY & ROLEPLAY
    # ========================================================================
    details = character.get('details', {})
    vals['PersonalityTraits '] = details.get('personality', '')  # trailing space!
    vals['Ideals'] = details.get('ideal', '')
    vals['Bonds'] = details.get('bond', '')
    vals['Flaws'] = details.get('flaw', '')
    
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
    # SPELLCASTING (PAGE 3)
    # ========================================================================
    spellcasting = character.get('spellcasting')
    
    # First, clear ALL spell fields and prepared checkboxes
    for field in CANTRIP_FIELDS:
        vals[field] = ""
    for level in range(1, 10):
        for field in SPELL_FIELDS_BY_LEVEL.get(level, []):
            vals[field] = ""
            # Clear prepared checkbox
            if field in SPELL_FIELD_TO_PREP_CHECKBOX:
                cb[SPELL_FIELD_TO_PREP_CHECKBOX[field]] = False
    
    if spellcasting:
        vals['Spellcasting Class 2'] = spellcasting.get('class', '')
        vals['SpellcastingAbility 2'] = spellcasting.get('ability', '').upper()[:3]
        vals['SpellSaveDC  2'] = str(spellcasting.get('spell_save_dc', ''))  # two spaces!
        vals['SpellAtkBonus 2'] = format_modifier(spellcasting.get('spell_attack_bonus', 0))
        
        # Spell slots (levels 1-9 -> fields 19-27)
        spell_slots = spellcasting.get('spell_slots', {})
        for lv_num in range(1, 10):
            key = f'level_{lv_num}'
            field_idx = 18 + lv_num  # 19..27
            if key in spell_slots:
                vals[f'SlotsTotal {field_idx}'] = str(spell_slots[key].get('total', 0))
                vals[f'SlotsRemaining {field_idx}'] = str(spell_slots[key].get('remaining', 0))
            else:
                vals[f'SlotsTotal {field_idx}'] = ''
                vals[f'SlotsRemaining {field_idx}'] = ''
        
        # Partition spells by level
        cantrips = []
        spells_by_level = {lv: [] for lv in range(1, 10)}
        
        # Get cantrips from cantrips_known
        for entry in spellcasting.get('cantrips_known', []):
            if isinstance(entry, dict):
                cantrips.append(entry.get('name', ''))
            else:
                cantrips.append(str(entry))
        
        # Get leveled spells from spells_known
        # Also check for level 0 spells mixed in
        is_known_caster = class_name.lower() in KNOWN_SPELLS_CASTERS
        
        for spell in spellcasting.get('spells_known', []):
            lvl = spell.get('level', 0)
            name = spell.get('name', '')
            prepared = spell.get('prepared', False)
            
            if lvl == 0:
                if name not in cantrips:
                    cantrips.append(name)
            else:
                # For known-spells casters, treat all known spells as prepared
                if is_known_caster:
                    prepared = True
                spells_by_level[lvl].append({
                    'name': name,
                    'prepared': prepared
                })
        
        # Fill cantrip fields (no prepared checkboxes)
        for i, field in enumerate(CANTRIP_FIELDS):
            if i < len(cantrips):
                vals[field] = cantrips[i]
            else:
                vals[field] = ""
        
        # Fill leveled spell fields + prepared checkboxes
        for level in range(1, 10):
            fields = SPELL_FIELDS_BY_LEVEL.get(level, [])
            spells = spells_by_level[level]
            
            for i, field in enumerate(fields):
                if i < len(spells):
                    spell = spells[i]
                    vals[field] = spell['name']
                    # Set prepared checkbox
                    if field in SPELL_FIELD_TO_PREP_CHECKBOX:
                        cb[SPELL_FIELD_TO_PREP_CHECKBOX[field]] = spell['prepared']
                else:
                    vals[field] = ""
                    if field in SPELL_FIELD_TO_PREP_CHECKBOX:
                        cb[SPELL_FIELD_TO_PREP_CHECKBOX[field]] = False
    else:
        # Non-caster: blank all spell slots
        for lv_num in range(1, 10):
            field_idx = 18 + lv_num
            vals[f'SlotsTotal {field_idx}'] = ''
            vals[f'SlotsRemaining {field_idx}'] = ''
    
    return vals, cb


# ============================================================================
# OUTPUT DIRECTORY MANAGEMENT
# ============================================================================

def clean_output_dir(out_folder):
    """Delete all old generated PDFs in the output folder"""
    out_path = Path(out_folder)
    if out_path.exists():
        for pdf_file in out_path.glob("*.pdf"):
            pdf_file.unlink()
    out_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MAIN CLI FUNCTION
# ============================================================================

def generate_character_sheet(character_json_path, output_folder="generated_character_sheets"):
    """
    Main function to generate and fill a character sheet PDF.
    
    Usage:
        python generate_character.py --character path/to/character.json
    """
    
    # Load character
    print(f"Loading character from {character_json_path}...")
    with open(character_json_path, 'r', encoding='utf-8') as f:
        character = json.load(f)
    
    # Clean output folder (delete old PDFs)
    print(f"Cleaning output folder: {output_folder}")
    clean_output_dir(output_folder)
    
    # Generate output filename
    char_name = character['name'].replace(" ", "")
    level = character['classes'][0]['level']
    output_filename = f"{char_name}_Level{level}.pdf"
    output_file = Path(output_folder) / output_filename
    
    # Load PDF template
    script_dir = Path(__file__).parent
    pdf_template = script_dir / "assets" / "5E_CharacterSheet_Fillable.pdf"
    print(f"Loading PDF template from {pdf_template}...")
    reader = PdfReader(str(pdf_template))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    
    # Build field values
    print("Calculating D&D 5e stats and building field mappings...")
    text_vals, checkbox_vals = build_field_values(character)
    
    # Fill text fields
    print(f"Filling {len(text_vals)} text fields...")
    for page in writer.pages:
        writer.update_page_form_field_values(page, text_vals)
    
    # Fill checkboxes
    checked_count = sum(1 for v in checkbox_vals.values() if v)
    print(f"Setting {checked_count} checkboxes (of {len(checkbox_vals)} total)...")
    set_checkboxes(writer, checkbox_vals)
    
    # Ensure fields are visible (NeedAppearances)
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)}
        )
    
    # Write output
    print(f"Writing filled PDF to {output_file}...")
    with open(output_file, "wb") as f:
        writer.write(f)
    
    print()
    print("=" * 60)
    print("SUCCESS! Character sheet generated!")
    print("=" * 60)
    print(f"Character: {character['name']}")
    print(f"Class: {character['classes'][0]['name']} {level}")
    print(f"Text fields filled: {len(text_vals)}")
    print(f"Checkboxes checked: {checked_count}")
    print(f"Output: {output_file}")
    print("=" * 60)
    
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
