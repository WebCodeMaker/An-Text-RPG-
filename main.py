from rpg.game import RPGGame, load_game


def main() -> None:
    print("Welcome to Chronicles of Emberfall")
    choice = input("Load existing save? (y/N) ").strip().lower()
    game = load_game() if choice == "y" else None
    if game is None:
        hero_name = input("Name your hero: ").strip() or "Aria"
        game = RPGGame.new_game(hero_name)
    game.run()


if __name__ == "__main__":
    main()
