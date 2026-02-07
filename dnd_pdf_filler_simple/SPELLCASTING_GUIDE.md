# D&D 5e Spellcasting Rules - Character Sheet Filler

## Overview

This document explains how spellcasting works in D&D 5e and how the Character Sheet Filler implements these rules.

## Spellcasting Ability

Different classes use different ability scores for spellcasting:

| Class | Spellcasting Ability |
|-------|---------------------|
| Wizard, Artificer | Intelligence (INT) |
| Cleric, Druid, Ranger | Wisdom (WIS) |
| Bard, Paladin, Sorcerer, Warlock | Charisma (CHA) |

## Spell Save DC & Attack Bonus

These are calculated automatically:

```
Spell Save DC = 8 + Proficiency Bonus + Spellcasting Ability Modifier
Spell Attack Bonus = Proficiency Bonus + Spellcasting Ability Modifier
```

**Example**: Level 5 Wizard with INT 16
- INT modifier = +3
- Proficiency bonus = +3
- Spell Save DC = 8 + 3 + 3 = **14**
- Spell Attack Bonus = 3 + 3 = **+6**

## Cantrips Known

Cantrips are level 0 spells that can be cast at will.

| Class | Cantrips at Level 1 | Cantrips at Level 4 | Cantrips at Level 10 |
|-------|---------------------|---------------------|----------------------|
| Wizard | 3 | 4 | 5 |
| Sorcerer | 4 | 5 | 6 |
| Bard | 2 | 3 | 4 |
| Cleric | 3 | 4 | 5 |
| Druid | 2 | 3 | 4 |
| Warlock | 2 | 3 | 4 |

**Example**: Level 5 Wizard knows **4 cantrips**

## Spells Known vs. Spells Prepared

### Classes that Prepare Spells (Wizard, Cleric, Druid, Paladin)

These classes have a **spellbook** or know all spells on their class list, but can only prepare a limited number each day.

**Number of Prepared Spells = Spellcasting Ability Modifier + Class Level**

**Wizard at Level 5 with INT 16:**
- INT modifier = +3
- Can prepare: 3 + 5 = **8 spells**

**Spells in Spellbook:**
- Start with 6 level 1 spells at character creation
- Learn 2 new spells per level (can be any level you can cast)
- Can copy spells from scrolls/other spellbooks

**Example Progression:**
- Level 1: 6 spells in book, prepare 4-5
- Level 2: 8 spells in book, prepare 5-6
- Level 3: 10 spells in book, prepare 6-7
- Level 4: 12 spells in book, prepare 7-8
- Level 5: 14 spells in book, prepare 8-9

### Classes that Know Spells (Sorcerer, Bard, Warlock, Ranger)

These classes have a fixed number of spells known and always have them "prepared".

**Sorcerer Spells Known:**
| Level | Spells Known |
|-------|--------------|
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |
| 4 | 5 |
| 5 | 6 |

**Bard Spells Known:**
| Level | Spells Known |
|-------|--------------|
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |
| 4 | 7 |
| 5 | 8 |

## Spell Slots

Spell slots determine how many spells you can cast before resting.

### Full Casters (Wizard, Sorcerer, Cleric, Druid, Bard)

| Level | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | 2 | - | - | - | - | - | - | - | - |
| 2 | 3 | - | - | - | - | - | - | - | - |
| 3 | 4 | 2 | - | - | - | - | - | - | - |
| 4 | 4 | 3 | - | - | - | - | - | - | - |
| 5 | 4 | 3 | 2 | - | - | - | - | - | - |
| 6 | 4 | 3 | 3 | - | - | - | - | - | - |
| 7 | 4 | 3 | 3 | 1 | - | - | - | - | - |
| 8 | 4 | 3 | 3 | 2 | - | - | - | - | - |
| 9 | 4 | 3 | 3 | 3 | 1 | - | - | - | - |
| 10 | 4 | 3 | 3 | 3 | 2 | - | - | - | - |

### Half Casters (Paladin, Ranger)

| Level | 1st | 2nd | 3rd | 4th | 5th |
|-------|-----|-----|-----|-----|-----|
| 1 | - | - | - | - | - |
| 2 | 2 | - | - | - | - |
| 3 | 3 | - | - | - | - |
| 4 | 3 | - | - | - | - |
| 5 | 4 | 2 | - | - | - |
| 6 | 4 | 2 | - | - | - |
| 7 | 4 | 3 | - | - | - |
| 8 | 4 | 3 | - | - | - |
| 9 | 4 | 3 | 2 | - | - |
| 10 | 4 | 3 | 2 | - | - |

### Warlock (Pact Magic)

Warlocks use a different system:

| Level | Spell Slots | Slot Level |
|-------|-------------|------------|
| 1 | 1 | 1st |
| 2 | 2 | 1st |
| 3 | 2 | 2nd |
| 4 | 2 | 2nd |
| 5 | 2 | 3rd |
| 6 | 2 | 3rd |
| 7-8 | 2 | 4th |
| 9-10 | 2 | 5th |
| 11-16 | 3 | 5th |
| 17-20 | 4 | 5th |

**Note**: Warlocks regain spell slots on **short rest**, not just long rest.

## Character Sheet JSON Format

### For Prepared Casters (Wizard, Cleric)

```json
{
    "spellcasting": {
        "class": "Wizard",
        "ability": "Intelligence",
        "spell_save_dc": 14,
        "spell_attack_bonus": 6,
        "cantrips_known": [
            "Fire Bolt",
            "Mage Hand",
            "Prestidigitation",
            "Ray of Frost"
        ],
        "spells_known": [
            {
                "name": "Magic Missile",
                "level": 1,
                "prepared": true,
                "ritual": false
            },
            {
                "name": "Alarm",
                "level": 1,
                "prepared": false,
                "ritual": true
            }
        ],
        "spell_slots": {
            "level_1": {"total": 4, "remaining": 4},
            "level_2": {"total": 3, "remaining": 3},
            "level_3": {"total": 2, "remaining": 2}
        }
    }
}
```

### For Known Casters (Sorcerer, Bard)

```json
{
    "spellcasting": {
        "class": "Sorcerer",
        "ability": "Charisma",
        "spell_save_dc": 14,
        "spell_attack_bonus": 6,
        "cantrips_known": [
            "Fire Bolt",
            "Light",
            "Mage Hand",
            "Prestidigitation"
        ],
        "spells_known": [
            {
                "name": "Magic Missile",
                "level": 1,
                "prepared": true,
                "ritual": false
            },
            {
                "name": "Shield",
                "level": 1,
                "prepared": true,
                "ritual": false
            }
        ],
        "spell_slots": {
            "level_1": {"total": 4, "remaining": 2},
            "level_2": {"total": 3, "remaining": 3},
            "level_3": {"total": 2, "remaining": 0}
        }
    }
}
```

## Example: Level 5 Wizard

**Character Stats:**
- Level: 5
- Intelligence: 16 (+3 modifier)
- Proficiency Bonus: +3

**Calculated Values:**
- Spell Save DC: 8 + 3 + 3 = **14**
- Spell Attack Bonus: 3 + 3 = **+6**
- Cantrips Known: **4** (from Wizard table)
- Spells in Spellbook: 6 (starting) + 8 (2 per level × 4 levels) = **14 spells**
- Spells Prepared: 3 + 5 = **8 spells**

**Spell Slots:**
- 1st level: 4 slots
- 2nd level: 3 slots
- 3rd level: 2 slots

**Spellbook Contents (14 total):**

*Level 1 (10 spells):*
1. Alarm (ritual)
2. Burning Hands
3. Charm Person
4. Comprehend Languages (ritual)
5. Detect Magic (ritual)
6. Disguise Self
7. False Life
8. Feather Fall
9. Find Familiar (ritual)
10. Fog Cloud

*Level 2 (4 spells):*
11. Hold Person
12. Invisibility
13. Misty Step
14. Web

**Prepared Spells (8 total):**
1. Burning Hands (1)
2. Detect Magic (1, ritual)
3. Grease (1)
4. Mage Armor (1)
5. Magic Missile (1)
6. Shield (1)
7. Hold Person (2)
8. Misty Step (2)

## Ritual Spells

Ritual spells can be cast without using a spell slot if you have an extra 10 minutes. Wizards can cast any ritual spell in their spellbook, even if not prepared.

**Example**: A Wizard can cast *Detect Magic* or *Find Familiar* as rituals without preparing them, as long as they're in the spellbook.

## Multi-Classing (Not Currently Supported)

Multi-classing combines spell slots but not spells known. This is complex and not implemented in the current MVP.

## Validation Checklist

When creating a spellcaster character:

✅ **Cantrips**: Check class table for correct number  
✅ **Spells Known**: 
   - Wizard: 6 + (2 × [level - 1])
   - Sorcerer: Use class table
   - Bard: Use class table
✅ **Spells Prepared**:
   - Wizard/Cleric/Druid: Ability mod + level
   - Sorcerer/Bard: All known spells are always available
✅ **Spell Slots**: Use appropriate table (full/half/pact magic)  
✅ **Spell Save DC**: 8 + proficiency + ability mod  
✅ **Spell Attack Bonus**: proficiency + ability mod  
✅ **Spell Levels**: Can only know/prepare spells of levels you can cast

## Resources

- **Player's Handbook (PHB)**: Official spellcasting rules
- **SRD 5.2**: Complete spell list with correct spell names
- **D&D Beyond**: Online character builder with spell automation

## Implementation Notes

The `fill_character_sheet_complete.py` script:
- Automatically calculates spell DC and attack bonus
- Properly handles spell slot progression for all caster types
- Formats spells with level indicators and markers:
  - `(Cantrip)` for cantrips
  - `(1)`, `(2)`, `(3)` for spell levels
  - `[P]` for prepared spells
  - `[R]` for ritual spells
- Example: `"Fireball (3) [P]"` = Level 3 prepared spell
