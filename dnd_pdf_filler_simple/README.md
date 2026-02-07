# D&D 5e PDF Character Sheet Filler

A Python tool that automatically fills D&D 5e character sheet PDFs with all available fields using accurate D&D 5e rule calculations.

## 🚀 Quick Start

### Generate a Character Sheet

```bash
python generate_character.py --character examples/Character.fighter.level3.json
```

This will:
- Load your character JSON file
- Calculate all D&D 5e stats and modifiers
- Fill 80-140+ PDF fields (depending on whether your character is a spellcaster)
- Save to `generated_character_sheets/<CharacterName>_Level<Level>.pdf`

### Usage in Python

```python
from generate_character import generate_character_sheet

# Generate a single character
output_path = generate_character_sheet("examples/Character.fighter.level3.json")
print(f"Created: {output_path}")

# Use a custom output folder
output_path = generate_character_sheet(
    "examples/Character.wizard.level3.json", 
    output_folder="my_characters"
)
```

## ✨ Features

✅ **Complete Field Coverage**: Fills 80-140+ PDF fields
- Character metadata (name, class, race, background, alignment)
- Ability scores and modifiers
- Saving throws and skills
- Armor class, hit points, proficiency bonus
- Weapons and attacks
- Currency and equipment
- Personality traits, ideals, bonds, flaws
- Features and feats
- **Full spellcasting support** (cantrips, leveled spells, spell slots, spell DC)

✅ **Accurate D&D 5e Rules**:
- Proficiency bonuses (based on character level)
- Ability modifiers and saving throws
- Skill bonus calculations with proficiency
- Full spellcaster support (Wizard, Sorcerer, Cleric, Druid, Bard)
- Half-caster support (Paladin, Ranger, Artificer)
- Warlock support (pact magic)
- Non-spellcasters (Fighter, Barbarian, Rogue, Monk)

✅ **Smart Spellcasting**:
- Spell count calculated: `level + spellcasting_ability_modifier`
- Cantrips separated from leveled spells
- Spell slots calculated per class progression
- Support for prepared vs known spells
- Ritual and prepared spell markers

✅ **Validation**:
- Ensures personality traits field is populated
- Validates spell counts match character level
- Automatic spell list truncation if needed

## 📁 Project Structure

```
dnd_pdf_filler_simple/
├── generate_character.py          # Main CLI (NEW!)
├── fill_character_sheet_complete.py # Original complete implementation
├── fill_character_sheet.py         # Original simple version
├── list_pdf_fields.py             # PDF field extractor
├── README.md                       # This file
├── requirements.txt               # Python dependencies
│
├── examples/
│   ├── Character.fighter.level3.json    # Fighter example (NEW!)
│   ├── Character.wizard.level3.json     # Wizard example (NEW!)
│   ├── Character.complete.json          # Fighter level 5 (legacy)
│   ├── Character.spellcaster.json       # Wizard level 5 (legacy)
│   └── Character.sample.json            # Original example
│
├── generated_character_sheets/    # Output folder (auto-created)
│   ├── ThorinIronforge_Level3.pdf  # Generated Fighter PDF
│   └── ElarionStarweaver_Level3.pdf # Generated Wizard PDF
│
├── assets/
│   └── 5E_CharacterSheet_Fillable.pdf  # Blank D&D 5E sheet
│
├── srd-5.2-spells.json            # SRD 5.2 spell database
│
└── docs/
    ├── COMPLETE_GUIDE.md          # JSON schema reference
    ├── SPELLCASTING_GUIDE.md      # D&D 5e spellcasting rules
    └── IMPLEMENTATION_SUMMARY.md  # Technical overview
```

## 💾 Installation

```bash
pip install -r requirements.txt
```

## 📖 Usage

### Command Line

```bash
# Generate from JSON file
python generate_character.py --character examples/Character.fighter.level3.json

# Use custom output folder
python generate_character.py --character examples/Character.wizard.level3.json --out-folder my_sheets

# Get help
python generate_character.py --help
```

### Python Module

```python
from generate_character import generate_character_sheet

# Basic usage
pdf_path = generate_character_sheet("path/to/character.json")

# With custom output folder
pdf_path = generate_character_sheet(
    "path/to/character.json",
    output_folder="my_characters"
)

print(f"Generated: {pdf_path}")
```

## 📋 Character JSON Format

### Minimal Example

```json
{
  "name": "Thorin Ironforge",
  "player": {"name": "Your Name"},
  "classes": [{"name": "Fighter", "level": 3, "hit_die": 10}],
  "race": {"name": "Mountain Dwarf", "size": "Medium", "speed": 25},
  "background": {"name": "Soldier", "feature": "Military Rank"},
  "alignment": "Lawful Neutral",
  "ability_scores": {
    "str": 18, "dex": 14, "con": 16,
    "int": 10, "wis": 12, "cha": 8
  },
  "armor_class": {"value": 18},
  "hit_points": {"max": 31, "current": 31},
  "hit_dice": {"total": "3d10", "current": "3"},
  "saving_throws": {"str": false, "dex": false, "con": true, "int": false, "wis": false, "cha": false},
  "skills": {"Athletics": true, "Perception": true},
  "details": {
    "personality": "I am unfailingly loyal to my friends",
    "ideal": "A well-conducted war is noble",
    "bond": "I will always remember my first battle",
    "flaw": "I have little respect for anyone who is not a proven warrior"
  },
  "weapons": [
    {"name": "Longsword", "attack_bonus": 6, "damage": "1d8+4", "damage_type": "slashing"}
  ]
}
```

### Spellcasting Support

For characters with spellcasting abilities, add the `spellcasting` section:

```json
{
  "spellcasting": {
    "class": "Wizard",
    "ability": "Intelligence",
    "spell_save_dc": 13,
    "spell_attack_bonus": 5,
    "spell_slots": {
      "level_1": {"total": 4, "remaining": 4},
      "level_2": {"total": 2, "remaining": 2}
    },
    "cantrips_known": [
      {"name": "Fire Bolt", "level": 0},
      {"name": "Mage Hand", "level": 0}
    ],
    "spells_known": [
      {"name": "Fire Bolt", "level": 0, "prepared": true},
      {"name": "Magic Missile", "level": 1, "prepared": true},
      {"name": "Sleep", "level": 1, "prepared": false},
      {"name": "Scorching Ray", "level": 2, "prepared": true}
    ]
  }
}
```

See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for the full schema with 130+ fields.

## 📊 Examples

The `examples/` folder contains complete reference characters:

### Level 3 Fighter (Non-Spellcaster)
```bash
python generate_character.py --character examples/Character.fighter.level3.json
```

Generates: `generated_character_sheets/ThorinIronforge_Level3.pdf`
- 88 PDF fields filled
- Longsword, shield, and crossbow
- Proficiency in Athletics, Perception

### Level 3 Wizard (Full Spellcaster)
```bash
python generate_character.py --character examples/Character.wizard.level3.json
```

Generates: `generated_character_sheets/ElarionStarweaver_Level3.pdf`
- 101 PDF fields filled
- 3 cantrips (Fire Bolt, Mage Hand, Prestidigitation)
- 6 leveled spells (calculated as 3 level + 3 INT modifier)
- Spell slots: 4 L1, 2 L2

## 📋 Output

Generated PDFs are saved to `generated_character_sheets/` with filename:
```
<CharacterName>_Level<Level>.pdf
```

Examples:
- `ThorinIronforge_Level3.pdf`
- `ElarionStarweaver_Level3.pdf`

## 🎯 D&D 5e Rules Reference

### Spell Count Calculation

For most spellcasters, the number of spells known is:
```
spells_known = character_level + spellcasting_ability_modifier
```

Example: Level 3 Wizard with INT 16 (+3 modifier)
```
spells_known = 3 + 3 = 6 spells known
```

Special cases:
- **Warlock**: Uses fixed progression (pact magic - not affected by ability modifier)
- **Sorcerer**: Fixed table per level (unaffected by CHA modifier)
- **Bard**: Fixed table per level
- **Artificer**: Fixed table per level

### Proficiency Bonus by Level

| Level | Prof | Level | Prof |
|-------|------|-------|------|
| 1-4   | +2   | 13-16 | +5   |
| 5-8   | +3   | 17-20 | +6   |
| 9-12  | +4   |       |      |

### Spell Slots by Class

**Full Casters** (Wizard, Cleric, Druid, Sorcerer, Bard):
- Level 1: 2 L1 slots
- Level 3: 4 L1, 2 L2 slots
- Level 5: 4 L1, 3 L2, 2 L3 slots

**Half-Casters** (Paladin, Ranger):
- Level 1-4: No spells
- Level 5: 4 L1, 2 L2 slots

**Artificer**:
- Same as half-casters

**Warlock** (Pact Magic):
- Uses spell slots but regain on short rest
- Different level progression than other casters

See [SPELLCASTING_GUIDE.md](SPELLCASTING_GUIDE.md) for complete progressions.

## 🛠️ Technical Details

### Core Functions

- `generate_character_sheet()` - Main entry point
- `build_field_values()` - Maps JSON to PDF fields
- `validate_character()` - Validates character data
- `ability_mod()` - Calculates ability modifiers
- `prof_bonus()` - Calculates proficiency bonus
- `skill_bonus()` - Calculates skill bonuses
- `calculate_spells_known()` - Calculates spell count per class rules
- `get_spell_slots()` - Returns spell slots per class/level

### Spell Slot Tables

- `FULL_CASTER_SLOTS` - Wizard, Sorcerer, Cleric, Druid, Bard progressions
- `HALF_CASTER_SLOTS` - Paladin, Ranger progressions
- `ARTIFICER_SLOTS` - Artificer progression
- `WARLOCK_SLOTS` - Warlock pact magic slots

### PDF Field Mapping

The tool maps character JSON fields to 200+ named PDF fields in the character sheet:

- **Identity**: CharacterName, PlayerName, ClassLevel, Race, Background
- **Abilities**: STR, DEX, CON, INT, WIS, CHA (+ modifiers)
- **Skills**: Acrobatics, Athletics, Arcana... (all 18)
- **Combat**: AC, Initiative, Speed, HP, HD, Inspiration
- **Weapons**: Wpn Name, Wpn AtkBonus, Wpn Damage (up to 3 weapons)
- **Spellcasting**: Spellcasting Class, Ability, Save DC, Attack Bonus
- **Spells**: Spells 1010X, SlotsTotal, SlotsRemaining (all levels)
- **Personality**: PersonalityTraits, Ideals, Bonds, Flaws
- **Equipment**: Equipment, Currency, Features, Backstory

## 🔧 Requirements

- Python 3.6+
- PyPDF2 (for PDF field manipulation)

## 📚 Documentation

- **COMPLETE_GUIDE.md** - Full JSON schema with 130+ field descriptions
- **SPELLCASTING_GUIDE.md** - D&D 5e spellcasting rules and progressions
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details

## 🐛 Troubleshooting

### Issue: PDF not opening
**Solution**: Ensure `assets/5E_CharacterSheet_Fillable.pdf` exists in the correct location

### Issue: Fields not filled
**Solution**: 
- Verify personality traits field is non-empty
- Check character JSON for required fields
- Ensure ability scores are present for calculations

### Issue: Spell count validation warnings
**Solution**:
- Verify `level + spellcasting_ability_modifier` matches your intent
- See SPELLCASTING_GUIDE.md for class-specific rules
- Tool will auto-truncate excess spells (deterministic order)

## 📝 License

MIT

## 🤝 Contributing

To add support for new features:
1. Update the JSON schema in COMPLETE_GUIDE.md
2. Add mapping logic to `build_field_values()` in generate_character.py
3. Add validation rules to `validate_character()`
4. Test with example character
5. Update documentation

## 🎓 References

- D&D 5e Player's Handbook (PHB)
- D&D 5e Official Character Sheet
- SRD 5.2 Spell Database
