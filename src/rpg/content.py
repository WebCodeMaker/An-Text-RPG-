from __future__ import annotations

from typing import Dict, List
import random

from .models import Character, Item, Player, Skill


SKILLS: Dict[str, Skill] = {
    "Slash": Skill("Slash", mana_cost=0, min_damage=4, max_damage=8),
    "Fireball": Skill("Fireball", mana_cost=7, min_damage=9, max_damage=15, status_effect="Burn"),
    "Heal": Skill("Heal", mana_cost=6, min_damage=0, max_damage=0, heal_ratio=0.28),
    "Shadow Strike": Skill("Shadow Strike", mana_cost=10, min_damage=12, max_damage=20),
}

ITEMS: Dict[str, Item] = {
    "Potion": Item("Potion", "consumable", value=15, power=24, description="Restore 24 HP."),
    "Ether": Item("Ether", "consumable", value=20, power=15, description="Restore 15 Mana."),
    "Iron Sword": Item("Iron Sword", "weapon", value=45, power=4, description="A balanced blade."),
    "Mage Staff": Item("Mage Staff", "weapon", value=55, power=6, description="Amplifies magical attacks."),
    "Leather Armor": Item("Leather Armor", "armor", value=40, power=3, description="Light defensive gear."),
    "Knight Armor": Item("Knight Armor", "armor", value=80, power=6, description="Heavy steel protection."),
}

QUESTS = {
    "Goblin Menace": {
        "goal": 4,
        "target": "Goblin",
        "reward_gold": 70,
        "reward_xp": 90,
    },
    "Ashen Threat": {
        "goal": 2,
        "target": "Ash Drake",
        "reward_gold": 120,
        "reward_xp": 150,
    },
}


def create_player(name: str) -> Player:
    return Player(
        name=name,
        level=1,
        hp=85,
        max_hp=85,
        mana=30,
        max_mana=30,
        strength=11,
        defense=5,
        agility=7,
        crit_chance=0.12,
        skills=[SKILLS["Slash"], SKILLS["Fireball"], SKILLS["Heal"]],
        inventory={"Potion": 2, "Ether": 1},
        quest_progress={k: 0 for k in QUESTS},
    )


def generate_enemy(zone: str, player_level: int) -> Character:
    if zone == "Ember Woods":
        table = [
            ("Goblin", 1.0, 36, 7, 2, 0.07),
            ("Wolf", 1.1, 42, 9, 3, 0.09),
            ("Ash Drake", 1.35, 58, 12, 4, 0.1),
        ]
    else:
        table = [
            ("Bandit", 1.2, 52, 11, 5, 0.12),
            ("Wraith", 1.4, 60, 13, 6, 0.15),
            ("Ancient Guardian", 1.8, 88, 16, 8, 0.18),
        ]

    name, scale, hp, strength, defense, crit = random.choice(table)
    level = max(1, int(player_level * scale))
    return Character(
        name=name,
        level=level,
        hp=hp + level * 4,
        max_hp=hp + level * 4,
        mana=0,
        max_mana=0,
        strength=strength + level,
        defense=defense + level // 2,
        agility=5 + level,
        crit_chance=crit,
        skills=[],
    )


def shop_inventory() -> List[Item]:
    return [
        ITEMS["Potion"],
        ITEMS["Ether"],
        ITEMS["Iron Sword"],
        ITEMS["Mage Staff"],
        ITEMS["Leather Armor"],
        ITEMS["Knight Armor"],
    ]
