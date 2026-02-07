# D&D 5e Character Sheet PDF Filler - Complete MVP

## Overview

This tool fills **ALL available fields** in the official D&D 5e character sheet PDF (AcroForm) using a structured Character JSON file. It implements complete D&D 5e rules with accurate calculations for:

- Ability modifiers
- Proficiency bonuses
- Skill bonuses
- Saving throws
- Spell slots (all caster types)
- Spell save DC & attack bonus
- Passive perception
- And more...

## Features

✅ **Complete field coverage** - Maps to all 200+ PDF fields  
✅ **D&D 5e rule accuracy** - Follows PHB calculations exactly  
✅ **Full spellcasting support** - Handles all spell slots, cantrips, prepared spells  
✅ **Multiple character types** - Works with fighters, spellcasters, etc.  
✅ **Comprehensive JSON schema** - Includes physical description, equipment, backstory, etc.

## Files

- `fill_character_sheet_complete.py` - Complete MVP script with full field mapping
- `examples/Character.complete.json` - Fighter example (non-spellcaster)
- `examples/Character.spellcaster.json` - Wizard example (full spellcaster)
- `examples/Character.sample.json` - Original simple example

## Usage

### Basic Usage

```bash
python fill_character_sheet_complete.py \
  --pdf assets/5E_CharacterSheet_Fillable.pdf \
  --character examples/Character.complete.json \
  --out filled_character.pdf
```

### Arguments

- `--pdf` - Path to the blank D&D 5e character sheet PDF
- `--character` - Path to your character JSON file
- `--out` - Output filename (default: `filled_character.pdf`)

### Examples

Fill a Fighter character:
```bash
python fill_character_sheet_complete.py \
  --pdf assets/5E_CharacterSheet_Fillable.pdf \
  --character examples/Character.complete.json \
  --out fighter.pdf
```

Fill a Wizard character:
```bash
python fill_character_sheet_complete.py \
  --pdf assets/5E_CharacterSheet_Fillable.pdf \
  --character examples/Character.spellcaster.json \
  --out wizard.pdf
```

## JSON Schema

### Required Fields

```json
{
  "name": "Character Name",
  "player": {
    "name": "Player Name"
  },
  "race": {
    "name": "Race Name",
    "subtype": null
  },
  "classes": [{
    "name": "Class Name",
    "subtype": "Subclass",
    "level": 5,
    "hit_die": 10,
    "spellcasting": null
  }],
  "background": {
    "name": "Background Name",
    "feature": "Feature Name"
  },
  "alignment": "Alignment",
  "experience_points": 0,
  "ability_scores": {
    "str": 10, "dex": 10, "con": 10,
    "int": 10, "wis": 10, "cha": 10
  },
  "saving_throws": {
    "str": false, "dex": false, "con": false,
    "int": false, "wis": false, "cha": false
  },
  "skills": {
    "Acrobatics": false,
    "Animal Handling": false,
    "Arcana": false,
    "Athletics": false,
    "Deception": false,
    "History": false,
    "Insight": false,
    "Intimidation": false,
    "Investigation": false,
    "Medicine": false,
    "Nature": false,
    "Perception": false,
    "Performance": false,
    "Persuasion": false,
    "Religion": false,
    "Sleight of Hand": false,
    "Stealth": false,
    "Survival": false
  },
  "armor_class": {
    "value": 10,
    "description": "Description"
  },
  "speed": {
    "Walk": 30
  },
  "hit_points": {
    "max": 10,
    "current": 10,
    "temp": 0
  },
  "hit_dice": {
    "total": "1d10",
    "current": 1
  },
  "details": {
    "personality": "Personality traits",
    "ideal": "Ideals",
    "bond": "Bonds",
    "flaw": "Flaws"
  }
}
```

### Optional Fields

#### Physical Description
```json
"physical": {
  "age": 25,
  "height": "6'0\"",
  "weight": "180 lbs",
  "eyes": "Blue",
  "skin": "Fair",
  "hair": "Brown"
}
```

#### Currency
```json
"currency": {
  "cp": 0,
  "sp": 0,
  "ep": 0,
  "gp": 0,
  "pp": 0
}
```

#### Combat
```json
"initiative_bonus": 2,
"inspiration": false,
"proficiency_bonus": 2,
"passive_perception": 10
```

#### Weapons
```json
"weapons": [{
  "name": "Longsword",
  "attack_bonus": 5,
  "damage": "1d8+3",
  "damage_type": "Slashing",
  "properties": ["Versatile (1d10)"],
  "equipped": true
}]
```

#### Equipment & Items
```json
"equipment": [
  "Backpack",
  "Rope (50 ft)",
  "Rations (10 days)"
],
"attacks_and_spellcasting": "Special abilities text",
"treasure": "Notable treasure and magic items"
```

#### Proficiencies
```json
"languages": ["Common", "Elvish"],
"proficiencies": [
  "All armor",
  "Martial weapons"
]
```

#### Features
```json
"features_and_traits": [
  "Darkvision: 60 feet",
  "Second Wind: Regain 1d10+5 HP"
],
"feats": []
```

#### Background & Story
```json
"allies_and_organizations": "Allied groups and contacts",
"faction": {
  "name": "Faction Name",
  "symbol": null
},
"backstory": "Character's full backstory"
```

#### Spellcasting (for spellcasters)
```json
"spellcasting": {
  "class": "Wizard",
  "ability": "Intelligence",
  "spell_save_dc": 14,
  "spell_attack_bonus": 6,
  "cantrips_known": [
    "Fire Bolt",
    "Mage Hand"
  ],
  "spells_known": [
    {
      "name": "Magic Missile",
      "level": 1,
      "prepared": true,
      "ritual": false
    }
  ],
  "spell_slots": {
    "level_1": {
      "total": 4,
      "remaining": 4
    },
    "level_2": {
      "total": 3,
      "remaining": 2
    }
  }
}
```

## D&D 5e Calculations

The script implements these rules automatically:

### Ability Modifier
```
modifier = (ability_score - 10) // 2
```

### Proficiency Bonus
```
Level 1-4:   +2
Level 5-8:   +3
Level 9-12:  +4
Level 13-16: +5
Level 17-20: +6
```

### Skill Bonus
```
skill_bonus = ability_modifier + (proficiency_bonus if proficient)
```

### Saving Throw
```
save_bonus = ability_modifier + (proficiency_bonus if proficient)
```

### Spell Save DC
```
DC = 8 + proficiency_bonus + spellcasting_ability_modifier
```

### Spell Attack Bonus
```
attack = proficiency_bonus + spellcasting_ability_modifier
```

### Passive Perception
```
passive = 10 + perception_skill_bonus
```

### Initiative
```
initiative = DEX modifier
```

## PDF Field Coverage

The script fills **ALL** available PDF fields:

### Identity (10 fields)
- Character Name (both pages)
- Player Name
- Class & Level
- Background
- Race
- Alignment
- Age, Height, Weight
- Eyes, Skin, Hair
- XP

### Ability Scores (12 fields)
- STR, DEX, CON, INT, WIS, CHA
- All 6 modifiers

### Saving Throws (6 fields)
- All 6 ability saves with calculated bonuses

### Skills (18 fields)
- All 18 skills with calculated bonuses

### Combat Stats (13 fields)
- AC, Initiative, Speed
- HP Max, Current, Temp
- Hit Dice Total & Current
- Inspiration
- Proficiency Bonus
- Passive Perception

### Currency (5 fields)
- CP, SP, EP, GP, PP

### Weapons (9 fields)
- 3 weapon slots (name, attack bonus, damage)
- Attacks & Spellcasting text

### Personality (4 fields)
- Personality Traits
- Ideals
- Bonds
- Flaws

### Story & Background (6 fields)
- Backstory
- Allies & Organizations
- Faction Name
- Treasure
- Proficiencies & Languages
- Features & Traits

### Spellcasting (50+ fields)
- Spellcasting Class
- Spellcasting Ability
- Spell Save DC
- Spell Attack Bonus
- Spell Slots (levels 1-9, total & remaining)
- Spell Names (100+ fields for individual spells)

### Equipment (1 field)
- Equipment list

## Supported Classes

### Full Casters
- Wizard
- Sorcerer
- Cleric
- Druid
- Bard

### Half Casters
- Paladin
- Ranger
- Artificer

### Special
- Warlock (Pact Magic)

### Non-Casters
- Fighter
- Barbarian
- Rogue
- Monk

## Implementation Notes

### Correctness Priority
The code prioritizes correctness over optimization:
- Explicit calculations following PHB
- Clear variable names
- No premature optimization
- Comprehensive comments

### Field Naming
PDF field names are used exactly as extracted:
- `CHamod` (not `CHAmod`)
- `DEXmod ` (with trailing space)
- `SpellSaveDC  2` (with double space)

These quirks are preserved for accuracy.

### Spell Slots
Spell slots are calculated using standard 5e progression tables:
- Full casters use standard progression
- Half casters (Paladin/Ranger) use half progression
- Artificer uses unique progression
- Warlock uses Pact Magic system

### Spell Name Fields
Spells are filled into fields sequentially:
1. Cantrips listed first with "(Cantrip)" suffix
2. Leveled spells with level number: "(1)", "(2)", etc.
3. Prepared spells marked with "[P]"
4. Ritual spells marked with "[R]"

Example: `"Fireball (3) [P]"` = 3rd level prepared spell

## Testing

The package includes two complete test characters:

### Fighter (Non-Caster)
- `Character.complete.json`
- Thorin Ironforge, Mountain Dwarf Fighter 5
- Demonstrates: Combat stats, weapons, non-spellcasting features
- Fields filled: ~88

### Wizard (Full Caster)
- `Character.spellcaster.json`
- Elarion Starweaver, High Elf Wizard 5
- Demonstrates: Full spellcasting, spell slots, prepared spells
- Fields filled: ~131

## Dependencies

```
PyPDF2
```

Install with:
```bash
pip install PyPDF2
```

## Output

The script provides progress output:
```
Loading character from examples/Character.complete.json...
Loading PDF from assets/5E_CharacterSheet_Fillable.pdf...
Calculating D&D 5e stats and building field mappings...
Filling 88 fields...
Writing filled PDF to filled_fighter.pdf...
✓ Complete! Character sheet filled successfully.
  Character: Thorin Ironforge
  Class: Fighter 5
  Fields filled: 88
```

## Future Enhancements

Potential improvements for future versions:
- Multi-class support
- Character images
- Faction symbols
- Auto-calculation from minimal input
- Validation and error checking
- JSON schema validation
- Web interface
- Character builder UI

## License

Hackathon MVP - Use freely for personal projects.

## Credits

Built for D&D 5e using the official WotC character sheet PDF.
Implements Player's Handbook rules (5th Edition).
