# Usage Examples

This document provides practical examples of using the D&D 5e Character Sheet PDF Filler.

## Prerequisites

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Obtain a fillable D&D 5e character sheet PDF (AcroForm format). The official D&D 5e character sheet PDF from Wizards of the Coast or similar fillable PDFs work well.

## Basic Usage

### Example 1: Fighter Character

Fill a character sheet for Thorin Oakenshield (Fighter):

```bash
python fill_character_sheet.py character_sheet.pdf Character.json filled_thorin.pdf
```

This will:
- Load `Character.json` (included - a level 3 Fighter)
- Read the fillable PDF fields from `character_sheet.pdf`
- Calculate all derived stats (modifiers, bonuses, etc.)
- Write the completed PDF to `filled_thorin.pdf`

### Example 2: Wizard Character

Fill a character sheet for Elara Moonwhisper (Wizard with spellcasting):

```bash
python fill_character_sheet.py character_sheet.pdf Character_Wizard.json filled_elara.pdf
```

This will:
- Load `Character_Wizard.json` (included - a level 5 Wizard)
- Calculate spellcasting stats (Spell Save DC, Spell Attack Bonus)
- Fill all relevant fields including spellcasting information

## What Gets Filled

The tool automatically fills these PDF fields:

### Identity & Background
- Character Name
- Player Name
- Race
- Class & Level
- Alignment
- Personality Traits
- Ideals
- Bonds
- Flaws

### Ability Scores
- STR, DEX, CON, INT, WIS, CHA (scores)
- All ability modifiers (automatically calculated)

### Combat Stats
- Armor Class (AC)
- Initiative (calculated from DEX modifier)
- Speed
- Hit Points (current and max)

### Proficiency
- Proficiency Bonus (calculated from level)

### Saving Throws
- All six saving throw bonuses (calculated)
- Proficiency checkboxes (marked if proficient)

### Skills
- All 18 skill bonuses (calculated)
- Proficiency checkboxes (marked if proficient)
- Passive Perception (calculated)

### Weapons
- Up to 2 weapons with:
  - Name
  - Attack Bonus
  - Damage (dice + type)

### Spellcasting (if applicable)
- Spellcasting Class
- Spellcasting Ability
- Spell Save DC (calculated)
- Spell Attack Bonus (calculated)

## How Calculations Work

### Example: Level 3 Fighter with STR 16

**Character Data:**
- Level: 3
- STR Score: 16
- Athletics: Proficient

**Calculations:**
1. **STR Modifier:** (16 - 10) // 2 = +3
2. **Proficiency Bonus:** Level 3 = +2
3. **Athletics Skill:** +3 (STR) + 2 (proficient) = +5

### Example: Level 5 Wizard with INT 17

**Character Data:**
- Level: 5
- INT Score: 17
- Spellcasting Stat: INT

**Calculations:**
1. **INT Modifier:** (17 - 10) // 2 = +3
2. **Proficiency Bonus:** Level 5 = +3
3. **Spell Save DC:** 8 + 3 (prof) + 3 (INT) = 14
4. **Spell Attack Bonus:** +3 (prof) + 3 (INT) = +6

## Customizing Your Character

To create your own character:

1. Copy `Character.json` or `Character_Wizard.json`
2. Edit the JSON with your character's information
3. Run the script with your custom JSON file

### Key Fields to Edit

```json
{
  "name": "Your Character Name",
  "player": { "name": "Your Name" },
  "race": { "name": "Your Race" },
  "classes": [
    {
      "name": "Your Class",
      "level": 1,
      "hit_die": "d10",
      "spellcasting_stat": "INT"  // or null for non-casters
    }
  ],
  "ability_scores": {
    "STR": 10,  // Your ability scores
    "DEX": 10,
    "CON": 10,
    "INT": 10,
    "WIS": 10,
    "CHA": 10
  },
  "skills": {
    "Athletics": true,  // Set to true for proficient skills
    "Acrobatics": false
    // ... etc
  },
  "saving_throws": {
    "STR": true,  // Set to true for proficient saves
    "DEX": false
    // ... etc
  }
  // ... other fields
}
```

## Troubleshooting

### "Input PDF not found" Error
Make sure you have a fillable D&D 5e character sheet PDF in the correct location.

### "Character JSON not found" Error
Check that your JSON file path is correct and the file exists.

### Fields Not Filling Correctly
Different PDF character sheets may use different field names. The script is designed for standard D&D 5e official character sheets. If using a custom sheet, you may need to:
1. Check the PDF field names using a PDF editor
2. Adjust the field mapping in `fill_character_sheet.py`

### Import Errors
Make sure you've installed the requirements:
```bash
pip install -r requirements.txt
```

## Testing the Implementation

Run the test suite to verify all D&D 5e calculations:

```bash
python test_rules.py
```

This will test:
- Ability modifier calculations
- Proficiency bonus calculations
- Saving throw calculations
- Skill bonus calculations
- Initiative calculations
- Passive Perception calculations
- Spell calculations
- Full derived stats computation

All tests should pass with green checkmarks.

## Advanced Usage

### Using in a Script

You can import and use the functions in your own Python scripts:

```python
from fill_character_sheet import (
    load_character_data,
    compute_derived_stats,
    fill_character_sheet
)

# Load character
character = load_character_data('Character.json')

# Compute stats
stats = compute_derived_stats(character)
print(f"Proficiency Bonus: +{stats['proficiency_bonus']}")
print(f"Initiative: {stats['initiative']}")

# Fill PDF
fill_character_sheet('input.pdf', 'output.pdf', character)
```

### Batch Processing

Fill multiple character sheets:

```bash
for char in Character*.json; do
    output="filled_${char}"
    python fill_character_sheet.py character_sheet.pdf "$char" "$output"
done
```

## Support

For issues or questions:
1. Check that your JSON follows the correct format
2. Verify your PDF is a fillable AcroForm
3. Run the test suite to ensure calculations are correct
4. Review the README.md for additional information
