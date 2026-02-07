import json, argparse, os, shutil
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject


# ============================================================================
# D&D 5E RULES – CALCULATIONS
# ============================================================================

def ability_mod(score):
    """Calculate ability modifier from ability score."""
    return (score - 10) // 2


def prof_bonus(level):
    """Calculate proficiency bonus from character level."""
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


def fmt(value):
    """Format a modifier with +/- sign."""
    return f"+{value}" if value >= 0 else str(value)


# ============================================================================
# SPELL FIELD MAPPING  (official WotC 5e fillable PDF)
# ============================================================================

# Cantrip fields (level 0) - NO prepared checkboxes
_CANTRIP_FIELDS = [
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
_SPELL_FIELDS_BY_LEVEL = {
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
_SPELL_FIELD_TO_PREP_CHECKBOX = {
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

# "Known spells" casters - treat all known spells as prepared for MVP
_KNOWN_SPELLS_CASTERS = ["sorcerer", "bard", "warlock", "ranger"]

# Class → spellcasting ability key
_CASTING_ABILITY = {
    "wizard": "int", "artificer": "int",
    "cleric": "wis", "druid": "wis", "ranger": "wis",
    "bard": "cha", "sorcerer": "cha", "paladin": "cha", "warlock": "cha",
}

# Skill → (PDF field name, ability key)   — field names include trailing spaces
# where the real PDF has them.
_SKILL_MAP = {
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

# Saving-throw proficiency checkboxes (page 1)
_ST_CHECKBOX = {
    "str": "Check Box 11",
    "dex": "Check Box 18",
    "con": "Check Box 19",
    "int": "Check Box 20",
    "wis": "Check Box 21",
    "cha": "Check Box 22",
}

# Skill proficiency checkboxes (page 1, top-to-bottom order)
_SKILL_CHECKBOX = {
    "Acrobatics":      "Check Box 23",
    "Animal Handling": "Check Box 24",
    "Arcana":          "Check Box 25",
    "Athletics":       "Check Box 26",
    "Deception":       "Check Box 27",
    "History":         "Check Box 28",
    "Insight":         "Check Box 29",
    "Intimidation":    "Check Box 30",
    "Investigation":   "Check Box 31",
    "Medicine":        "Check Box 32",
    "Nature":          "Check Box 33",
    "Perception":      "Check Box 34",
    "Performance":     "Check Box 35",
    "Persuasion":      "Check Box 36",
    "Religion":        "Check Box 37",
    "Sleight of Hand": "Check Box 38",
    "Stealth":         "Check Box 39",
    "Survival":        "Check Box 40",
}

# Death-save checkboxes
_DEATH_SUCCESS_CB = ["Check Box 12", "Check Box 13", "Check Box 14"]
_DEATH_FAILURE_CB = ["Check Box 15", "Check Box 16", "Check Box 17"]

# Inspiration checkbox (not same as spell prepared checkbox!)
_INSPIRATION_CB = "Check Box 251"


# ============================================================================
# SPELL HELPERS
# ============================================================================

def _get_spellcasting_ability_mod(character):
    class_name = character["classes"][0]["name"].lower()
    ability_key = _CASTING_ABILITY.get(class_name)
    if ability_key is None:
        sc = character.get("spellcasting", {})
        ability_key = sc.get("ability", "").lower()[:3]
    score = character["ability_scores"].get(ability_key, 10)
    return ability_mod(score)


def _partition_spells(spellcasting, class_name):
    """
    Return {level_int: [{name, prepared}, ...]} with cantrips at key 0.
    For known-spells casters, treat all spells as prepared.
    """
    by_level = {i: [] for i in range(10)}
    is_known_caster = class_name.lower() in _KNOWN_SPELLS_CASTERS

    for entry in spellcasting.get("cantrips_known", []):
        name = entry["name"] if isinstance(entry, dict) else entry
        by_level[0].append({"name": name, "prepared": False})  # cantrips have no prepared checkbox

    for sp in spellcasting.get("spells_known", []):
        lvl = sp.get("level", 0)
        name = sp.get("name", "")
        prepared = sp.get("prepared", False)
        
        # For known-spells casters, treat all known spells as prepared
        if is_known_caster:
            prepared = True
        
        if lvl == 0:
            if name not in [s["name"] for s in by_level[0]]:
                by_level[0].append({"name": name, "prepared": False})
            continue
        by_level[lvl].append({"name": name, "prepared": prepared})

    return by_level


def _enforce_spell_limit(by_level, character):
    """Truncate levelled spells to character_level + casting_mod."""
    class_level = character["classes"][0]["level"]
    casting_mod = _get_spellcasting_ability_mod(character)
    limit = max(1, class_level + casting_mod)

    budget = limit
    for lv in range(1, 10):
        if budget <= 0:
            by_level[lv] = []
        elif len(by_level[lv]) > budget:
            by_level[lv] = by_level[lv][:budget]
            budget = 0
        else:
            budget -= len(by_level[lv])


def _build_spell_field_vals(by_level, checkbox_vals):
    """
    Map spell names into the correct PDF section fields.
    Also set prepared checkboxes for leveled spells.
    """
    vals = {}
    
    # Clear all spell fields first
    for field in _CANTRIP_FIELDS:
        vals[field] = ""
    for level in range(1, 10):
        for field in _SPELL_FIELDS_BY_LEVEL.get(level, []):
            vals[field] = ""
            if field in _SPELL_FIELD_TO_PREP_CHECKBOX:
                checkbox_vals[_SPELL_FIELD_TO_PREP_CHECKBOX[field]] = False
    
    # Fill cantrip fields (no prepared checkboxes)
    cantrips = by_level.get(0, [])
    for i, field in enumerate(_CANTRIP_FIELDS):
        if i < len(cantrips):
            vals[field] = cantrips[i]["name"]
        else:
            vals[field] = ""
    
    # Fill leveled spell fields + prepared checkboxes
    for level in range(1, 10):
        fields = _SPELL_FIELDS_BY_LEVEL.get(level, [])
        spells = by_level.get(level, [])
        
        for i, field in enumerate(fields):
            if i < len(spells):
                spell = spells[i]
                vals[field] = spell["name"]
                # Set prepared checkbox
                if field in _SPELL_FIELD_TO_PREP_CHECKBOX:
                    checkbox_vals[_SPELL_FIELD_TO_PREP_CHECKBOX[field]] = spell["prepared"]
            else:
                vals[field] = ""
                if field in _SPELL_FIELD_TO_PREP_CHECKBOX:
                    checkbox_vals[_SPELL_FIELD_TO_PREP_CHECKBOX[field]] = False
    
    return vals


# ============================================================================
# CHECKBOX HELPER
# ============================================================================

def _set_checkboxes(writer, checkbox_vals):
    """
    Toggle checkbox annotations directly in the page tree.
    checkbox_vals: {field_name: bool}
    """
    for page in writer.pages:
        if "/Annots" not in page:
            continue
        for annot_ref in page["/Annots"]:
            annot = annot_ref.get_object()
            field_name = annot.get("/T")
            if field_name is None:
                continue
            # Convert PyPDF2 string
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
# BUILD COMPLETE FIELD VALUES
# ============================================================================

def build_all_vals(c):
    """
    Build the complete PDF-field → value dictionary from a character dict.
    Returns (vals_dict, by_level_snapshot, checkbox_vals).
    """
    cls = c["classes"][0]
    level = cls["level"]
    pb = prof_bonus(level)

    # Ability scores & modifiers
    scores = c["ability_scores"]
    str_s, dex_s, con_s = scores["str"], scores["dex"], scores["con"]
    int_s, wis_s, cha_s = scores["int"], scores["wis"], scores["cha"]
    str_m, dex_m, con_m = ability_mod(str_s), ability_mod(dex_s), ability_mod(con_s)
    int_m, wis_m, cha_m = ability_mod(int_s), ability_mod(wis_s), ability_mod(cha_s)
    mods = {"str": str_m, "dex": dex_m, "con": con_m,
            "int": int_m, "wis": wis_m, "cha": cha_m}

    vals = {}

    # ------------------------------------------------------------------
    # PAGE 1 – IDENTITY
    # ------------------------------------------------------------------
    vals["CharacterName"]   = c["name"]
    vals["CharacterName 2"] = c["name"]                          # page 2/3
    vals["PlayerName"]      = c.get("player", {}).get("name", "")
    vals["ClassLevel"]      = f"{cls['name']} {level}"
    vals["Background"]      = c.get("background", {}).get("name", "")
    vals["Race "]           = c["race"]["name"]                  # trailing space!
    vals["Alignment"]       = c.get("alignment", "")
    vals["XP"]              = str(c.get("experience_points", 0))

    # ------------------------------------------------------------------
    # ABILITY SCORES & MODIFIERS
    # ------------------------------------------------------------------
    vals["STR"]    = str(str_s)
    vals["DEX"]    = str(dex_s)
    vals["CON"]    = str(con_s)
    vals["INT"]    = str(int_s)
    vals["WIS"]    = str(wis_s)
    vals["CHA"]    = str(cha_s)
    vals["STRmod"] = fmt(str_m)
    vals["DEXmod "]= fmt(dex_m)      # trailing space!
    vals["CONmod"] = fmt(con_m)
    vals["INTmod"] = fmt(int_m)
    vals["WISmod"] = fmt(wis_m)
    vals["CHamod"] = fmt(cha_m)      # PDF typo – "CHa" not "CHA"

    # ------------------------------------------------------------------
    # PROFICIENCY BONUS & INSPIRATION
    # ------------------------------------------------------------------
    vals["ProfBonus"]   = fmt(pb)
    vals["Inspiration"] = "1" if c.get("inspiration", False) else ""

    # ------------------------------------------------------------------
    # SAVING THROWS  (value = modifier text; checkboxes handled separately)
    # ------------------------------------------------------------------
    st = c.get("saving_throws", {})
    st_keys = [("str", "ST Strength"),  ("dex", "ST Dexterity"),
               ("con", "ST Constitution"), ("int", "ST Intelligence"),
               ("wis", "ST Wisdom"),       ("cha", "ST Charisma")]
    for ab, field in st_keys:
        is_prof = st.get(ab, False)
        bonus = mods[ab] + (pb if is_prof else 0)
        vals[field] = fmt(bonus)

    # ------------------------------------------------------------------
    # SKILLS  (value = modifier text)
    # ------------------------------------------------------------------
    skills = c.get("skills", {})
    for skill_name, (pdf_field, ab) in _SKILL_MAP.items():
        is_prof = skills.get(skill_name, False)
        bonus = mods[ab] + (pb if is_prof else 0)
        vals[pdf_field] = fmt(bonus)

    # Passive Perception
    perc_prof = skills.get("Perception", False)
    perc_bonus = mods["wis"] + (pb if perc_prof else 0)
    vals["Passive"] = str(10 + perc_bonus)

    # ------------------------------------------------------------------
    # COMBAT STATS
    # ------------------------------------------------------------------
    vals["AC"]         = str(c.get("armor_class", {}).get("value", 10))
    vals["Initiative"] = fmt(c.get("initiative_bonus", dex_m))
    vals["Speed"]      = str(c.get("speed", {}).get("Walk", 30))

    hp = c.get("hit_points", {})
    vals["HPMax"]     = str(hp.get("max", 0))
    vals["HPCurrent"] = str(hp.get("current", hp.get("max", 0)))
    vals["HPTemp"]    = str(hp.get("temp", 0))

    hd = c.get("hit_dice", {})
    vals["HDTotal"] = str(hd.get("total", ""))
    vals["HD"]      = str(hd.get("current", ""))

    # ------------------------------------------------------------------
    # WEAPONS  (exact PDF field names with trailing spaces)
    # ------------------------------------------------------------------
    weapons = c.get("weapons", [])
    if len(weapons) > 0:
        w = weapons[0]
        vals["Wpn Name"]      = w["name"]
        vals["Wpn1 AtkBonus"] = fmt(w["attack_bonus"])
        vals["Wpn1 Damage"]   = f"{w['damage']} {w['damage_type']}"
    if len(weapons) > 1:
        w = weapons[1]
        vals["Wpn Name 2"]      = w["name"]
        vals["Wpn2 AtkBonus "]  = fmt(w["attack_bonus"])   # trailing space
        vals["Wpn2 Damage "]    = f"{w['damage']} {w['damage_type']}"  # trailing space
    if len(weapons) > 2:
        w = weapons[2]
        vals["Wpn Name 3"]       = w["name"]
        vals["Wpn3 AtkBonus  "]  = fmt(w["attack_bonus"])  # TWO trailing spaces
        vals["Wpn3 Damage "]     = f"{w['damage']} {w['damage_type']}"  # trailing space

    vals["AttacksSpellcasting"] = c.get("attacks_and_spellcasting", "")

    # ------------------------------------------------------------------
    # CURRENCY
    # ------------------------------------------------------------------
    cur = c.get("currency", {})
    vals["CP"] = str(cur.get("cp", 0))
    vals["SP"] = str(cur.get("sp", 0))
    vals["EP"] = str(cur.get("ep", 0))
    vals["GP"] = str(cur.get("gp", 0))
    vals["PP"] = str(cur.get("pp", 0))

    # ------------------------------------------------------------------
    # PERSONALITY
    # ------------------------------------------------------------------
    details = c.get("details", {})
    vals["PersonalityTraits "] = details.get("personality", "")  # trailing space!
    vals["Ideals"]             = details.get("ideal", "")
    vals["Bonds"]              = details.get("bond", "")
    vals["Flaws"]              = details.get("flaw", "")

    # ------------------------------------------------------------------
    # PROFICIENCIES & LANGUAGES
    # ------------------------------------------------------------------
    langs = c.get("languages", [])
    profs = c.get("proficiencies", [])
    prof_text = "Languages: " + ", ".join(langs)
    if profs:
        prof_text += "\n\nProficiencies: " + ", ".join(profs)
    vals["ProficienciesLang"] = prof_text

    # ------------------------------------------------------------------
    # EQUIPMENT
    # ------------------------------------------------------------------
    equip = c.get("equipment", [])
    vals["Equipment"] = "\n".join(equip) if equip else ""

    # ------------------------------------------------------------------
    # FEATURES & TRAITS
    # ------------------------------------------------------------------
    features = c.get("features_and_traits", [])
    feats = c.get("feats", [])
    feat_text = "\n\n".join(features)
    if feats:
        feat_text += "\n\nFeats:\n" + "\n".join(feats)
    vals["Feat+Traits"]          = feat_text
    vals["Features and Traits"]  = feat_text

    # ------------------------------------------------------------------
    # PAGE 2 – BACKSTORY / APPEARANCE
    # ------------------------------------------------------------------
    phys = c.get("physical", {})
    vals["Age"]    = str(phys.get("age", ""))
    vals["Height"] = str(phys.get("height", ""))
    vals["Weight"] = str(phys.get("weight", ""))
    vals["Eyes"]   = str(phys.get("eyes", ""))
    vals["Skin"]   = str(phys.get("skin", ""))
    vals["Hair"]   = str(phys.get("hair", ""))

    vals["Backstory"] = c.get("backstory", "")
    vals["Allies"]    = c.get("allies_and_organizations", "")
    vals["Treasure"]  = c.get("treasure", "")

    faction = c.get("faction", {})
    vals["FactionName"] = faction.get("name", "")

    # ------------------------------------------------------------------
    # CHECKBOXES
    # ------------------------------------------------------------------
    cb = {}

    # ------------------------------------------------------------------
    # SPELLCASTING  (page 3)
    # ------------------------------------------------------------------
    by_level_snapshot = {}
    spellcasting = c.get("spellcasting")

    # Clear all spell fields and prepared checkboxes first
    for field in _CANTRIP_FIELDS:
        vals[field] = ""
    for level in range(1, 10):
        for field in _SPELL_FIELDS_BY_LEVEL.get(level, []):
            vals[field] = ""
            if field in _SPELL_FIELD_TO_PREP_CHECKBOX:
                cb[_SPELL_FIELD_TO_PREP_CHECKBOX[field]] = False

    if spellcasting:
        vals["Spellcasting Class 2"]  = spellcasting.get("class", "")
        vals["SpellcastingAbility 2"] = spellcasting.get("ability", "").upper()[:3]
        vals["SpellSaveDC  2"]        = str(spellcasting.get("spell_save_dc", ""))    # two spaces!
        vals["SpellAtkBonus 2"]       = fmt(spellcasting.get("spell_attack_bonus", 0))

        # Spell slots (levels 1-9 → fields 19-27)
        slots = spellcasting.get("spell_slots", {})
        for lv_num in range(1, 10):
            key = f"level_{lv_num}"
            field_idx = 18 + lv_num        # 19..27
            if key in slots:
                vals[f"SlotsTotal {field_idx}"]     = str(slots[key].get("total", 0))
                vals[f"SlotsRemaining {field_idx}"] = str(slots[key].get("remaining", 0))
            else:
                vals[f"SlotsTotal {field_idx}"]     = ""
                vals[f"SlotsRemaining {field_idx}"] = ""

        # Partition spells by level, enforce limit, map to fields
        class_name = cls["name"]
        by_level = _partition_spells(spellcasting, class_name)
        _enforce_spell_limit(by_level, c)
        by_level_snapshot = {lv: [s["name"] for s in spells] for lv, spells in by_level.items()}
        vals.update(_build_spell_field_vals(by_level, cb))
    else:
        # For non-casters: blank all spell slots
        for lv_num in range(1, 10):
            field_idx = 18 + lv_num
            vals[f"SlotsTotal {field_idx}"]     = ""
            vals[f"SlotsRemaining {field_idx}"] = ""

    # Saving-throw proficiency
    for ab, cb_name in _ST_CHECKBOX.items():
        cb[cb_name] = st.get(ab, False)

    # Skill proficiency
    for skill_name, cb_name in _SKILL_CHECKBOX.items():
        cb[cb_name] = skills.get(skill_name, False)

    # Death saves
    ds = c.get("death_saves", {})
    successes = ds.get("successes", 0)
    failures  = ds.get("failures", 0)
    for i, cb_name in enumerate(_DEATH_SUCCESS_CB):
        cb[cb_name] = (i < successes)
    for i, cb_name in enumerate(_DEATH_FAILURE_CB):
        cb[cb_name] = (i < failures)

    # Inspiration
    cb[_INSPIRATION_CB] = c.get("inspiration", False)

    return vals, by_level_snapshot, cb


# ============================================================================
# OUTPUT DIRECTORY MANAGEMENT
# ============================================================================

def _clean_output_dir(out_path):
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if os.path.basename(out_dir) == "generated_character_sheets":
        shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)


# ============================================================================
# VALIDATION
# ============================================================================

def _validate(vals, out_path, by_level_snapshot):
    errors = []

    # PersonalityTraits must be populated
    pt = vals.get("PersonalityTraits ", "")
    if not pt or not pt.strip():
        errors.append("PersonalityTraits field is empty.")

    # Cantrips only in cantrip section
    cantrip_names = set(by_level_snapshot.get(0, []))
    for lvl in range(1, 10):
        for field in _SPELL_FIELDS_BY_LEVEL.get(lvl, []):
            v = vals.get(field, "")
            if v and v in cantrip_names:
                errors.append(f"Cantrip '{v}' in level-{lvl} section ({field}).")

    # Levelled spells not in cantrip section
    levelled = set()
    for lvl in range(1, 10):
        levelled.update(by_level_snapshot.get(lvl, []))
    for field in _CANTRIP_FIELDS:
        v = vals.get(field, "")
        if v and v in levelled:
            errors.append(f"Levelled spell '{v}' in cantrip section ({field}).")

    # Only one PDF in output directory
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if os.path.isdir(out_dir):
        pdfs = [f for f in os.listdir(out_dir) if f.lower().endswith(".pdf")]
        if len(pdfs) > 1:
            errors.append(f"Output dir has {len(pdfs)} PDFs: {pdfs}")

    if errors:
        raise RuntimeError("Validation failed:\n  • " + "\n  • ".join(errors))


# ============================================================================
# MAIN
# ============================================================================

def main():
    ap = argparse.ArgumentParser(description="Fill D&D 5e character sheet PDF")
    ap.add_argument("--pdf", required=True, help="Blank fillable PDF")
    ap.add_argument("--character", required=True, help="Character JSON")
    ap.add_argument("--out", default="generated_character_sheets/filled_character.pdf")
    a = ap.parse_args()

    with open(a.character, encoding="utf-8") as f:
        c = json.load(f)

    # Clean output directory
    _clean_output_dir(a.out)

    reader = PdfReader(a.pdf)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # Build every field value
    vals, by_level_snapshot, checkbox_vals = build_all_vals(c)

    # Fill text fields
    for page in writer.pages:
        writer.update_page_form_field_values(page, vals)

    # Fill checkboxes
    _set_checkboxes(writer, checkbox_vals)

    # Ensure NeedAppearances so viewers render the text
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)}
        )

    with open(a.out, "wb") as f:
        writer.write(f)

    # Post-write validation
    _validate(vals, a.out, by_level_snapshot)

    # Summary
    print(f"OK  {a.out}")
    print(f"  Character : {c['name']}")
    print(f"  Class     : {c['classes'][0]['name']} {c['classes'][0]['level']}")
    print(f"  Fields    : {len(vals)} text + {sum(checkbox_vals.values())} checkboxes")
    if by_level_snapshot:
        for lv in range(10):
            names = by_level_snapshot.get(lv, [])
            if names:
                label = "Cantrips" if lv == 0 else f"Level {lv}"
                print(f"  {label:10s}: {', '.join(names)}")


if __name__ == "__main__":
    main()
