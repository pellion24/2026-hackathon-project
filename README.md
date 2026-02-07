# D&D 5e Character Sheet PDF Filler

A Python tool that takes a structured D&D 5e Character.json object and programmatically fills out an official fillable D&D 5e character sheet PDF (AcroForm).

## Contributors
- Owen Norman
- Eason Barrineau
- Ashvij Hosdurg

## Stack
- Python 3
- PyPDF2

## Overview

This is an MVP tool built for a hackathon. It focuses on correctness, clarity, and successful PDF filling.

**Input:** Character.json (source of truth)  
**Output:** filled_character.pdf  
**Backend:** Python  
**PDF Type:** Fillable AcroForm (field-based)  
**Rule Set:** D&D 5e (SRD-compliant)

## Features

The tool:
- Loads a fillable D&D 5e character sheet PDF
- Reads form field names from the PDF
- Maps values from Character.json to PDF fields
- Computes derived values using standard D&D 5e rules
- Writes a completed PDF

### MVP Scope

The current implementation fills:
- ✅ Identity fields (name, player, race, class, alignment)
- ✅ Ability scores and modifiers
- ✅ HP, AC, speed, initiative
- ✅ Saving throws
- ✅ Skills with proficiency
- ✅ Passive Perception
- ✅ Personality traits, ideals, bonds, and flaws
- ✅ Weapons (up to 2)
- ✅ Spellcasting header values (save DC, attack bonus)

### D&D 5e Rules Implemented

The tool correctly applies these D&D 5e rules:

1. **Ability modifier** = (score − 10) // 2
2. **Proficiency bonus:**
   - Level 1–4 → +2
   - Level 5–8 → +3
   - Level 9–12 → +4
   - Level 13–16 → +5
   - Level 17–20 → +6
3. **Saving throw bonus** = Ability modifier + proficiency (if proficient)
4. **Skill bonus** = Ability modifier + proficiency (if proficient)
5. **Initiative** = DEX modifier
6. **Passive Perception** = 10 + Perception bonus
7. **Spell Save DC** = 8 + proficiency + spellcasting ability modifier
8. **Spell Attack Bonus** = proficiency + spellcasting ability modifier

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python fill_character_sheet.py <input_pdf> <character_json> [output_pdf]
```

### Example

```bash
python fill_character_sheet.py character_sheet.pdf Character.json filled_character.pdf
```

### Arguments

- `input_pdf` - Path to the fillable D&D 5e character sheet PDF (AcroForm)
- `character_json` - Path to your Character.json file
- `output_pdf` - (Optional) Output filename. Default: `filled_character.pdf`

## Character.json Format

The Character.json file should follow this structure:

```json
{
  "name": "Character Name",
  "player": {
    "name": "Player Name"
  },
  "race": {
    "name": "Race Name"
  },
  "classes": [
    {
      "name": "Class Name",
      "level": 3,
      "hit_die": "d10",
      "spellcasting_stat": null
    }
  ],
  "alignment": "Alignment",
  "ability_scores": {
    "STR": 16,
    "DEX": 12,
    "CON": 15,
    "INT": 10,
    "WIS": 13,
    "CHA": 8
  },
  "skills": {
    "Acrobatics": false,
    "Athletics": true,
    ...
  },
  "saving_throws": {
    "STR": true,
    "DEX": false,
    ...
  },
  "hit_points": {
    "max": 28,
    "current": 28
  },
  "armor_class": {
    "value": 16
  },
  "speed": {
    "Walk": 25
  },
  "details": {
    "personality": "Personality traits...",
    "ideal": "Ideals...",
    "bond": "Bonds...",
    "flaw": "Flaws..."
  },
  "weapons": [
    {
      "name": "Weapon Name",
      "attack_bonus": 5,
      "damage": "1d8+3",
      "damage_type": "slashing"
    }
  ],
  "spells": []
}
```

See `Character.json` for a complete example.

## Code Structure

The script is organized into three main sections:

1. **D&D 5e Rule Helper Functions** - Pure functions that implement D&D 5e math
2. **Skill to Ability Mapping** - Maps skills to their governing abilities
3. **PDF Filling Logic** - Loads data, computes stats, and fills the PDF

### Key Functions

- `ability_modifier(score)` - Calculate ability modifier
- `proficiency_bonus(level)` - Calculate proficiency bonus
- `saving_throw_bonus()` - Calculate saving throw bonus
- `skill_bonus()` - Calculate skill bonus
- `compute_derived_stats()` - Compute all derived values
- `fill_character_sheet()` - Main PDF filling function

## Requirements

- Python 3.6 or higher
- PyPDF2 3.0.1 or higher
- A fillable D&D 5e character sheet PDF (AcroForm format)

## Limitations

This is an MVP focused on core functionality. The following are intentionally not implemented:

- Inventory management
- Death saves
- Spell slot tracking
- Multi-page spell lists
- Equipment weight calculations
- Multi-class proficiency rules

## License

MIT

