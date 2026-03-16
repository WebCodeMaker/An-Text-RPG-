from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class Item:
    name: str
    kind: str  # consumable, weapon, armor
    value: int
    power: int = 0
    description: str = ""


@dataclass
class Skill:
    name: str
    mana_cost: int
    min_damage: int
    max_damage: int
    status_effect: Optional[str] = None
    heal_ratio: float = 0.0


@dataclass
class StatusEffect:
    name: str
    duration: int
    potency: int


@dataclass
class Character:
    name: str
    level: int
    hp: int
    max_hp: int
    mana: int
    max_mana: int
    strength: int
    defense: int
    agility: int
    crit_chance: float
    skills: List[Skill] = field(default_factory=list)
    statuses: List[StatusEffect] = field(default_factory=list)

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def attack_damage(self) -> int:
        base = random.randint(max(1, self.strength - 2), self.strength + 3)
        crit = random.random() < self.crit_chance
        if crit:
            return int(base * 1.6)
        return base

    def take_damage(self, amount: int) -> int:
        reduced = max(1, amount - self.defense)
        self.hp = max(0, self.hp - reduced)
        return reduced

    def apply_turn_statuses(self) -> List[str]:
        logs: List[str] = []
        remaining: List[StatusEffect] = []
        for status in self.statuses:
            if status.name == "Burn":
                self.hp = max(0, self.hp - status.potency)
                logs.append(f"{self.name} suffers {status.potency} burn damage.")
            elif status.name == "Regen":
                healed = min(self.max_hp - self.hp, status.potency)
                self.hp += healed
                logs.append(f"{self.name} regenerates {healed} HP.")
            status.duration -= 1
            if status.duration > 0:
                remaining.append(status)
        self.statuses = remaining
        return logs


@dataclass
class Player(Character):
    xp: int = 0
    gold: int = 30
    xp_to_next_level: int = 50
    inventory: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, Optional[Item]] = field(default_factory=lambda: {"weapon": None, "armor": None})
    quest_progress: Dict[str, int] = field(default_factory=dict)

    def grant_xp(self, amount: int) -> List[str]:
        logs = [f"You gain {amount} XP."]
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.35)
            hp_gain = random.randint(12, 18)
            mana_gain = random.randint(4, 8)
            self.max_hp += hp_gain
            self.max_mana += mana_gain
            self.strength += random.randint(2, 4)
            self.defense += random.randint(1, 3)
            self.agility += random.randint(1, 2)
            self.hp = self.max_hp
            self.mana = self.max_mana
            logs.append(f"Level up! You are now level {self.level}.")
            logs.append(f"Stats increased: +{hp_gain} HP, +{mana_gain} Mana.")
        return logs

    def equipped_bonus(self) -> Dict[str, int]:
        weapon_bonus = self.equipment["weapon"].power if self.equipment["weapon"] else 0
        armor_bonus = self.equipment["armor"].power if self.equipment["armor"] else 0
        return {"strength": weapon_bonus, "defense": armor_bonus}

    def to_save_data(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "strength": self.strength,
            "defense": self.defense,
            "agility": self.agility,
            "crit_chance": self.crit_chance,
            "xp": self.xp,
            "gold": self.gold,
            "xp_to_next_level": self.xp_to_next_level,
            "inventory": self.inventory,
            "equipment": {k: v.name if v else None for k, v in self.equipment.items()},
            "quest_progress": self.quest_progress,
        }
