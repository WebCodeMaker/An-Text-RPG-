from rpg.content import ITEMS, create_player
from rpg.game import RPGGame
from rpg.models import Character


def test_level_up_progression_increases_stats():
    player = create_player("Tester")
    player.grant_xp(1000)
    assert player.level > 1
    assert player.max_hp > 85
    assert player.max_mana > 30


def test_player_attack_defeats_enemy_over_time():
    game = RPGGame.new_game("Tester")
    enemy = Character(
        name="Dummy",
        level=1,
        hp=30,
        max_hp=30,
        mana=0,
        max_mana=0,
        strength=2,
        defense=1,
        agility=1,
        crit_chance=0,
        skills=[],
    )
    for _ in range(20):
        game._player_attack(enemy)
        if not enemy.is_alive:
            break
    assert enemy.hp == 0


def test_consumable_restores_health_and_mana(monkeypatch):
    game = RPGGame.new_game("Tester")
    game.player.hp = 10
    game.player.mana = 0

    monkeypatch.setattr("builtins.input", lambda _: "1")
    game._use_item(in_battle=True)
    assert game.player.hp > 10

    game.player.inventory["Ether"] = 1
    monkeypatch.setattr("builtins.input", lambda _: "2")
    game._use_item(in_battle=True)
    assert game.player.mana == ITEMS["Ether"].power
