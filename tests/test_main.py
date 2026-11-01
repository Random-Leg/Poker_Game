import random

import main
from game import GameState


def test_create_game_has_one_human_and_eight_bots():
    game = main.create_game()
    bots = main.create_bots()

    assert len(game.players) == 9
    assert game.get_human_player().name == "You"
    assert len(bots) == 8
    assert {p.name for p in game.players} - {"You"} == set(bots)


def test_play_hand_runs_to_completion_with_a_folding_human(monkeypatch, capsys):
    random.seed(11)
    game = main.create_game()
    bots = main.create_bots()
    monkeypatch.setattr("builtins.input", lambda _="": "fold")

    main.play_hand(game, bots)

    assert game.state == GameState.HAND_COMPLETE
    assert sum(p.chips for p in game.players) == 9000


def test_main_plays_several_hands_then_quits(monkeypatch, capsys):
    answers = iter(["fold"] * 200)
    # "fold" is a legal action on every turn; answer 'y' to continue twice
    # and then 'n'.  The continue prompt is recognisable by its text.
    continues = iter(["y", "y", "n"])

    def fake_input(prompt=""):
        if "another hand" in prompt:
            return next(continues)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    main.main(["--seed", "4"])

    output = capsys.readouterr().out
    assert "HAND #3" in output
    assert "Game over." in output


def test_quitting_mid_hand_exits_cleanly(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _="": "q")

    main.main(["--seed", "2"])

    assert "Game over." in capsys.readouterr().out
