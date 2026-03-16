from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List

from .content import ITEMS, QUESTS, create_player, generate_enemy, shop_inventory
from .models import Character, Item, Player, StatusEffect

SAVE_FILE = Path("savegame.json")


class RPGGame:
    def __init__(self, player: Player):
        self.player = player
        self.day = 1

    @classmethod
    def new_game(cls, name: str) -> "RPGGame":
        return cls(create_player(name))

    def run(self) -> None:
        print("\n=== Chronicles of Emberfall ===")
        while self.player.is_alive:
            print(f"\nDay {self.day} | {self.player.name} Lv{self.player.level} | HP {self.player.hp}/{self.player.max_hp} | Mana {self.player.mana}/{self.player.max_mana} | Gold {self.player.gold}")
            print("1) Explore Ember Woods  2) Explore Ruined Keep  3) Rest at Inn  4) Visit Shop")
            print("5) Show Inventory       6) Save Game            7) Quit")
            choice = input("> ").strip()
            if choice == "1":
                self.explore("Ember Woods")
            elif choice == "2":
                self.explore("Ruined Keep")
            elif choice == "3":
                self.rest()
            elif choice == "4":
                self.shop()
            elif choice == "5":
                self.show_inventory()
            elif choice == "6":
                self.save_game()
            elif choice == "7":
                print("Your legend pauses for now.")
                break
            else:
                print("Unknown option.")
            self.day += 1

        if not self.player.is_alive:
            print("You have fallen in battle. Game over.")

    def explore(self, zone: str) -> None:
        enemy = generate_enemy(zone, self.player.level)
        print(f"\nA level {enemy.level} {enemy.name} appears in the {zone}!")
        won = self.battle(enemy)
        if not won:
            return

        xp_gain = random.randint(20, 35) + enemy.level * 5
        gold_gain = random.randint(15, 25) + enemy.level * 3
        for msg in self.player.grant_xp(xp_gain):
            print(msg)
        self.player.gold += gold_gain
        print(f"You loot {gold_gain} gold.")
        self._update_quests(enemy.name)

    def battle(self, enemy: Character) -> bool:
        while enemy.is_alive and self.player.is_alive:
            for msg in self.player.apply_turn_statuses() + enemy.apply_turn_statuses():
                print(msg)

            print(f"\n{self.player.name}: HP {self.player.hp}/{self.player.max_hp}, Mana {self.player.mana}/{self.player.max_mana}")
            print(f"{enemy.name}: HP {enemy.hp}/{enemy.max_hp}")
            print("1) Attack  2) Skill  3) Use Item  4) Attempt Escape")
            action = input("Battle> ").strip()

            if action == "1":
                self._player_attack(enemy)
            elif action == "2":
                self._player_skill(enemy)
            elif action == "3":
                self._use_item(in_battle=True)
            elif action == "4":
                if random.random() < 0.45:
                    print("You escaped.")
                    return False
                print("Escape failed!")
            else:
                print("You hesitate and lose momentum.")

            if enemy.is_alive:
                self._enemy_turn(enemy)

        return self.player.is_alive

    def _player_attack(self, enemy: Character) -> None:
        bonus = self.player.equipped_bonus()["strength"]
        damage = self.player.attack_damage() + bonus
        dealt = enemy.take_damage(damage)
        print(f"You strike for {dealt} damage.")

    def _player_skill(self, enemy: Character) -> None:
        for i, skill in enumerate(self.player.skills, start=1):
            print(f"{i}) {skill.name} (Mana {skill.mana_cost})")
        pick = input("Skill> ").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= len(self.player.skills)):
            print("Invalid skill.")
            return

        skill = self.player.skills[int(pick) - 1]
        if self.player.mana < skill.mana_cost:
            print("Not enough mana.")
            return

        self.player.mana -= skill.mana_cost
        if skill.heal_ratio > 0:
            heal = max(8, int(self.player.max_hp * skill.heal_ratio))
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            print(f"You cast {skill.name} and recover {heal} HP.")
            return

        raw = random.randint(skill.min_damage, skill.max_damage) + self.player.level
        raw += self.player.equipped_bonus()["strength"]
        dealt = enemy.take_damage(raw)
        print(f"{skill.name} hits for {dealt} damage.")
        if skill.status_effect == "Burn" and random.random() < 0.5:
            enemy.statuses.append(StatusEffect("Burn", duration=3, potency=3 + self.player.level // 2))
            print(f"{enemy.name} is burning!")

    def _enemy_turn(self, enemy: Character) -> None:
        damage = enemy.attack_damage()
        reduced = max(1, damage - self.player.defense - self.player.equipped_bonus()["defense"])
        self.player.hp = max(0, self.player.hp - reduced)
        print(f"{enemy.name} attacks for {reduced} damage.")

    def _use_item(self, in_battle: bool = False) -> None:
        consumables = {k: v for k, v in self.player.inventory.items() if v > 0 and ITEMS[k].kind == "consumable"}
        if not consumables:
            print("You have no consumables.")
            return

        keys = list(consumables)
        for idx, item_name in enumerate(keys, start=1):
            print(f"{idx}) {item_name} x{self.player.inventory[item_name]}")
        pick = input("Item> ").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= len(keys)):
            print("Invalid item.")
            return
        item = ITEMS[keys[int(pick) - 1]]
        self.player.inventory[item.name] -= 1

        if item.name == "Potion":
            self.player.hp = min(self.player.max_hp, self.player.hp + item.power)
            print(f"Recovered {item.power} HP.")
        elif item.name == "Ether":
            self.player.mana = min(self.player.max_mana, self.player.mana + item.power)
            print(f"Recovered {item.power} Mana.")

        if not in_battle:
            print("You feel ready for adventure.")

    def rest(self) -> None:
        cost = 20
        if self.player.gold < cost:
            print("Not enough gold to rest.")
            return
        self.player.gold -= cost
        self.player.hp = self.player.max_hp
        self.player.mana = self.player.max_mana
        self.player.statuses.clear()
        print("A full rest restores your body and spirit.")

    def shop(self) -> None:
        while True:
            print("\n-- Merchant Caravan --")
            stock = shop_inventory()
            for i, item in enumerate(stock, start=1):
                print(f"{i}) {item.name} [{item.kind}] - {item.value}g ({item.description})")
            print("B) Back")
            pick = input("Shop> ").strip().lower()
            if pick == "b":
                return
            if not pick.isdigit() or not (1 <= int(pick) <= len(stock)):
                print("Invalid choice.")
                continue

            item = stock[int(pick) - 1]
            if self.player.gold < item.value:
                print("You can't afford that.")
                continue
            self.player.gold -= item.value
            if item.kind == "consumable":
                self.player.inventory[item.name] = self.player.inventory.get(item.name, 0) + 1
                print(f"Bought {item.name}.")
            else:
                self.player.equipment[item.kind] = item
                print(f"Equipped {item.name} immediately.")

    def show_inventory(self) -> None:
        print("\n-- Inventory --")
        if not self.player.inventory:
            print("(empty)")
        for item, qty in self.player.inventory.items():
            print(f"- {item}: {qty}")
        for slot, equipped in self.player.equipment.items():
            print(f"{slot.title()}: {equipped.name if equipped else 'None'}")
        print("\n-- Quests --")
        for quest_name, config in QUESTS.items():
            progress = self.player.quest_progress.get(quest_name, 0)
            print(f"{quest_name}: {progress}/{config['goal']} {config['target']} defeated")

        use = input("Use consumable now? (y/N) ").strip().lower()
        if use == "y":
            self._use_item(in_battle=False)

    def _update_quests(self, enemy_name: str) -> None:
        for quest_name, quest in QUESTS.items():
            if enemy_name == quest["target"]:
                self.player.quest_progress[quest_name] = self.player.quest_progress.get(quest_name, 0) + 1
                if self.player.quest_progress[quest_name] == quest["goal"]:
                    print(f"Quest complete: {quest_name}!")
                    self.player.gold += quest["reward_gold"]
                    for msg in self.player.grant_xp(quest["reward_xp"]):
                        print(msg)
                    print(f"Reward received: {quest['reward_gold']} gold.")

    def save_game(self) -> None:
        payload = {"player": self.player.to_save_data(), "day": self.day}
        SAVE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Game saved to {SAVE_FILE}.")


def load_game() -> RPGGame | None:
    if not SAVE_FILE.exists():
        return None
    data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    p = data["player"]
    player = create_player(p["name"])
    player.level = p["level"]
    player.hp = p["hp"]
    player.max_hp = p["max_hp"]
    player.mana = p["mana"]
    player.max_mana = p["max_mana"]
    player.strength = p["strength"]
    player.defense = p["defense"]
    player.agility = p["agility"]
    player.crit_chance = p["crit_chance"]
    player.xp = p["xp"]
    player.gold = p["gold"]
    player.xp_to_next_level = p["xp_to_next_level"]
    player.inventory = p["inventory"]
    player.quest_progress = p["quest_progress"]
    equipment = {}
    for slot, item_name in p["equipment"].items():
        equipment[slot] = ITEMS[item_name] if item_name else None
    player.equipment = equipment
    game = RPGGame(player)
    game.day = data.get("day", 1)
    return game
