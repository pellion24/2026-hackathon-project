# D&D 5e Rules Reference

This document provides a quick reference for the D&D 5e rules implemented in this tool.

## Core Mechanics

### Ability Scores
Six ability scores define your character's capabilities:
- **STR** (Strength) - Physical power
- **DEX** (Dexterity) - Agility and reflexes
- **CON** (Constitution) - Endurance
- **INT** (Intelligence) - Reasoning and memory
- **WIS** (Wisdom) - Awareness and insight
- **CHA** (Charisma) - Force of personality

Standard array: 15, 14, 13, 12, 10, 8

### Ability Modifiers

**Formula:** `(score - 10) // 2`

| Score | Modifier |
|-------|----------|
| 1     | -5       |
| 2-3   | -4       |
| 4-5   | -3       |
| 6-7   | -2       |
| 8-9   | -1       |
| 10-11 | 0        |
| 12-13 | +1       |
| 14-15 | +2       |
| 16-17 | +3       |
| 18-19 | +4       |
| 20-21 | +5       |
| 22-23 | +6       |

## Proficiency Bonus

**Formula:** Based on total character level

| Level   | Proficiency |
|---------|-------------|
| 1-4     | +2          |
| 5-8     | +3          |
| 9-12    | +4          |
| 13-16   | +5          |
| 17-20   | +6          |

## Saving Throws

**Formula:** `ability_modifier + proficiency_bonus (if proficient)`

Each class grants proficiency in two saving throws:
- **Barbarian:** STR, CON
- **Bard:** DEX, CHA
- **Cleric:** WIS, CHA
- **Druid:** INT, WIS
- **Fighter:** STR, CON
- **Monk:** STR, DEX
- **Paladin:** WIS, CHA
- **Ranger:** STR, DEX
- **Rogue:** DEX, INT
- **Sorcerer:** CON, CHA
- **Warlock:** WIS, CHA
- **Wizard:** INT, WIS

## Skills

**Formula:** `ability_modifier + proficiency_bonus (if proficient)`

Skills are based on specific abilities:

| Skill               | Ability | Example Use                      |
|---------------------|---------|----------------------------------|
| Acrobatics          | DEX     | Stay balanced, tumble            |
| Animal Handling     | WIS     | Calm an animal                   |
| Arcana              | INT     | Recall magic knowledge           |
| Athletics           | STR     | Climb, jump, swim                |
| Deception           | CHA     | Tell a convincing lie            |
| History             | INT     | Recall historical facts          |
| Insight             | WIS     | Determine intentions             |
| Intimidation        | CHA     | Influence through threats        |
| Investigation       | INT     | Look for clues                   |
| Medicine            | WIS     | Stabilize a dying companion      |
| Nature              | INT     | Recall nature knowledge          |
| Perception          | WIS     | Spot, hear, or detect something  |
| Performance         | CHA     | Delight an audience              |
| Persuasion          | CHA     | Influence through tact           |
| Religion            | INT     | Recall religious knowledge       |
| Sleight of Hand     | DEX     | Pick pockets, conceal objects    |
| Stealth             | DEX     | Hide or move silently            |
| Survival            | WIS     | Track, hunt, navigate wilderness |

## Combat Stats

### Armor Class (AC)
How hard you are to hit. Higher is better.

**Without armor:** 10 + DEX modifier  
**With armor:** Armor base + DEX modifier (limited by armor type)

### Initiative
Determines turn order in combat.

**Formula:** `DEX modifier`

### Hit Points (HP)
How much damage you can take before falling unconscious.

**At 1st level:** Max hit die + CON modifier  
**At higher levels:** Roll hit die (or take average) + CON modifier per level

Hit dice by class:
- **d6:** Sorcerer, Wizard
- **d8:** Bard, Cleric, Druid, Monk, Rogue, Warlock
- **d10:** Fighter, Paladin, Ranger
- **d12:** Barbarian

### Speed
How far you can move in a turn (in feet).

**Standard:** 30 ft  
**Dwarf, Halfling, Gnome:** 25 ft  
**Wood Elf, Monk (unarmored):** 35+ ft

## Passive Perception

Used by the DM to determine if you notice something without actively searching.

**Formula:** `10 + Perception skill bonus`

## Spellcasting

Only relevant for spellcasting classes.

### Spellcasting Ability
The ability score used for spellcasting:

- **Bard:** CHA
- **Cleric:** WIS
- **Druid:** WIS
- **Paladin:** CHA
- **Ranger:** WIS
- **Sorcerer:** CHA
- **Warlock:** CHA
- **Wizard:** INT

### Spell Save DC
The difficulty class for targets to resist your spells.

**Formula:** `8 + proficiency_bonus + spellcasting_ability_modifier`

### Spell Attack Bonus
Added to your d20 roll when making a spell attack.

**Formula:** `proficiency_bonus + spellcasting_ability_modifier`

## Example Calculations

### Example 1: Level 3 Fighter

**Character:**
- Level 3, STR 16, DEX 12
- Proficient in Athletics and STR/CON saves

**Calculations:**
- STR modifier: (16-10)//2 = **+3**
- DEX modifier: (12-10)//2 = **+1**
- Proficiency: Level 3 = **+2**
- STR save: 3 + 2 = **+5**
- DEX save: 1 (not proficient) = **+1**
- Athletics: 3 + 2 = **+5**
- Initiative: DEX mod = **+1**

### Example 2: Level 5 Wizard

**Character:**
- Level 5, INT 17, WIS 12
- Proficient in Arcana and INT/WIS saves
- Spellcasting ability: INT

**Calculations:**
- INT modifier: (17-10)//2 = **+3**
- WIS modifier: (12-10)//2 = **+1**
- Proficiency: Level 5 = **+3**
- INT save: 3 + 3 = **+6**
- WIS save: 1 + 3 = **+4**
- Arcana: 3 + 3 = **+6**
- Spell Save DC: 8 + 3 + 3 = **14**
- Spell Attack: 3 + 3 = **+6**

### Example 3: Passive Perception

**Character:**
- WIS 13 (modifier +1)
- Proficient in Perception
- Proficiency bonus +2

**Calculation:**
- Perception skill: 1 + 2 = **+3**
- Passive Perception: 10 + 3 = **13**

## Advantage/Disadvantage

Not directly calculated by this tool, but important to know:

**Advantage:** Roll two d20s, use the higher result  
**Disadvantage:** Roll two d20s, use the lower result

Common sources:
- Attacking while hidden: Advantage
- Attacking while prone: Disadvantage
- Attacking an invisible creature: Disadvantage

## References

This tool implements rules from the D&D 5e System Reference Document (SRD).

For complete rules, see:
- Player's Handbook (PHB)
- Basic Rules (free from Wizards of the Coast)
- System Reference Document (SRD) - Open Gaming License content
