# Chronicles of Emberfall (An-Text-RPG-)

A **feature-rich text RPG** playable from your terminal.

## Included RPG Systems
- Turn-based battle loop with normal attacks, skills, items, status effects, and escape chance.
- Leveling system with XP thresholds, stat growth, and full restore on level-up.
- Multiple zones with scaled random enemies.
- Inventory and equipment (weapon + armor) with stat bonuses.
- Merchant shop economy (buy consumables and gear with gold).
- Quest tracking and quest completion rewards.
- Save/load system via `savegame.json`.

## Quick Start
```bash
python -m pip install -e .
python main.py
```

## Controls
- Main menu: explore, rest, shop, inventory, save, quit.
- Battle menu: attack, use skill, use item, attempt escape.

## Testing
```bash
pytest -q
```

## Project Layout
- `main.py` – game entry point
- `src/rpg/models.py` – data models and progression rules
- `src/rpg/content.py` – skills, items, enemy tables, quests
- `src/rpg/game.py` – game loop, combat, shop, save/load
- `tests/test_systems.py` – regression tests for key mechanics
- `docs/README_GAMEPLAY.md` – advanced gameplay notes
