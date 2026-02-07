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
_ALL_SPELL_FIELDS = (
    [f"Spells 1010{i}" for i in range(10)] +      # indices 0-9
    [f"Spells {1014 + i}" for i in range(86)] +    # indices 10-95
    [f"Spells 10101{i}" for i in range(4)]          # indices 96-99
)

# (start_index, count) for each spell-level section in the PDF.
_SPELL_SECTION = {
    0: (0,  8),   # Cantrips
    1: (8,  12),  # Level 1
    2: (20, 13),  # Level 2
    3: (33, 13),  # Level 3
    4: (46, 13),  # Level 4
    5: (59, 9),   # Level 5
    6: (68, 9),   # Level 6
    7: (77, 9),   # Level 7
    8: (86, 7),   # Level 8
    9: (93, 7),   # Level 9
}

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

# Inspiration checkbox
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


def _partition_spells(spellcasting):
    """Return {level_int: [name, ...]} with cantrips at key 0."""
    by_level = {i: [] for i in range(10)}

    for entry in spellcasting.get("cantrips_known", []):
        name = entry["name"] if isinstance(entry, dict) else entry
        by_level[0].append(name)

    for sp in spellcasting.get("spells_known", []):
        lvl = sp["level"]
        if lvl == 0:
            if sp["name"] not in by_level[0]:
                by_level[0].append(sp["name"])
            continue
        by_level[lvl].append(sp["name"])

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


def _build_spell_field_vals(by_level):
    """Map spell names into the correct PDF section fields."""
    vals = {}
    for level in range(10):
        start, count = _SPELL_SECTION[level]
        fields = _ALL_SPELL_FIELDS[start:start + count]
        names = by_level.get(level, [])
        for i, field in enumerate(fields):
            vals[field] = names[i] if i < len(names) else ""
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
    # SPELLCASTING  (page 3)
    # ------------------------------------------------------------------
    by_level_snapshot = {}
    spellcasting = c.get("spellcasting")

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
        by_level = _partition_spells(spellcasting)
        _enforce_spell_limit(by_level, c)
        by_level_snapshot = {lv: list(names) for lv, names in by_level.items()}
        vals.update(_build_spell_field_vals(by_level))
    else:
        # For non-casters: blank all spell slots and fields
        for lv_num in range(1, 10):
            field_idx = 18 + lv_num
            vals[f"SlotsTotal {field_idx}"]     = ""
            vals[f"SlotsRemaining {field_idx}"] = ""

    # ------------------------------------------------------------------
    # CHECKBOXES
    # ------------------------------------------------------------------
    cb = {}

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
        s, cnt = _SPELL_SECTION[lvl]
        for field in _ALL_SPELL_FIELDS[s:s + cnt]:
            v = vals.get(field, "")
            if v and v in cantrip_names:
                errors.append(f"Cantrip '{v}' in level-{lvl} section ({field}).")

    # Levelled spells not in cantrip section
    levelled = set()
    for lvl in range(1, 10):
        levelled.update(by_level_snapshot.get(lvl, []))
    cs, cc = _SPELL_SECTION[0]
    for field in _ALL_SPELL_FIELDS[cs:cs + cc]:
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
