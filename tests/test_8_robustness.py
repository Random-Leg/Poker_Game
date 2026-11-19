"""Requirement group 8: robustness and state integrity (scripted input, output, seeds)."""
import builtins
import random

import pytest

import main
from betting import BettingAction as A
from game import GameState, QuitGame
from helpers import full_table, snapshot
from simulate import play_tournament


def scripted(monkeypatch, answers, on_call=None):
    """Replace input() with a list of answers; an exception in the list is raised."""
    queue = list(answers)
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        if on_call:
            on_call(len(prompts))
        item = queue.pop(0)
        if isinstance(item, type) and issubclass(item, BaseException):
            raise item()
        return item

    monkeypatch.setattr(builtins, "input", fake_input)
    return prompts


def human_to_act():
    """Hand 1 with the human sitting in the first seat to act (seat 3)."""
    game = full_table(human_seat=3)
    game.start_hand()
    assert game.current_player is game.get_human_player()
    return game


BAD_INPUT = ["xyz", "", "raise abc", "raise -5", "raise 999999", "bet 50", "check", "c 5"]


def test_bad_human_input_gets_a_message_and_a_new_prompt_without_changing_state(monkeypatch, capsys):
    # 8.1 every bad answer is refused; the turn is not lost and nothing moves
    game = human_to_act()
    before = snapshot(game)
    scripted(monkeypatch, BAD_INPUT + ["q"])
    with pytest.raises(QuitGame):
        game.human_turn()
    assert snapshot(game) == before
    assert capsys.readouterr().out.count("***") >= len(BAD_INPUT) - 1   # '' counts as invalid too
    # after all the mistakes a legal action still works
    scripted(monkeypatch, BAD_INPUT + ["call"])
    game.human_turn()
    assert game.pot.amount == 30 + 20 and game.current_player is not game.get_human_player()


@pytest.mark.parametrize("ending", [["q"], [EOFError], [KeyboardInterrupt]], ids=["q", "end-of-input", "ctrl-c"])
def test_quitting_ends_the_game_cleanly_with_the_final_standings(monkeypatch, capsys, ending):
    # 8.2
    scripted(monkeypatch, ending)
    # the human is seat 0; bots act first, so the first prompt is the human's turn
    main.main(["--seed", "3"])
    output = capsys.readouterr().out
    assert "Leaving the table" in output
    assert "Final chip leader" in output and "Game over." in output


def run_scripted_session(monkeypatch, capsys, seed):
    answers = {"hands": 0, "turns": 0}

    def fake_input(prompt=""):
        if "Play another hand" in prompt:
            answers["hands"] += 1
            return "y" if answers["hands"] < 3 else "n"
        answers["turns"] += 1
        # alternate check/call with fold, so a refused "c" (cannot afford the call) is followed by a legal fold
        return "c" if answers["turns"] % 2 else "f"

    monkeypatch.setattr(builtins, "input", fake_input)
    main.main(["--seed", str(seed)])
    return capsys.readouterr().out


def test_same_seed_and_same_input_give_identical_games(monkeypatch, capsys):
    # 8.5 identical deals, actions and results (three hands of output compared)
    first = run_scripted_session(monkeypatch, capsys, 5)
    second = run_scripted_session(monkeypatch, capsys, 5)
    other = run_scripted_session(monkeypatch, capsys, 6)
    assert first == second
    assert first != other
    assert first.count("HAND #") == 3


def test_bot_only_tournaments_finish_without_an_invariant_violation():
    # 8.3 invariants hold after every action of five seeded tournaments
    for seed in range(1, 6):
        assert play_tournament(seed)["finished"]


def test_hole_cards_of_bots_are_not_shown_before_showdown(monkeypatch, capsys):
    # 8.6 the human folds at once so the bots play the hand out
    scripted(monkeypatch, ["f"] * 5)
    random.seed(21)
    game, bots = main.create_game(), main.create_bots()
    main.play_hand(game, bots)
    output = capsys.readouterr().out
    before_showdown = output.split("=== SHOWDOWN ===")[0]
    human = game.get_human_player()
    assert f"Your cards: {game.format_cards(human.hand)}" in before_showdown
    for player in game.players:
        if player is not human:
            assert game.format_cards(player.hand) not in before_showdown, player.name
    assert "SHOWDOWN" in output or "wins" in output   # the hand really finished


def test_asking_for_the_probability_estimate_does_not_use_the_turn_or_change_the_state(monkeypatch, capsys):
    # 7.7 'p' prints an estimate, then the same player still has to act
    game = full_table(human_seat=3)
    game.start_hand()
    human = game.get_human_player()
    for _ in range(100):                    # play check/call to the flop, stopping at the human's turn
        if game.current_player is human and game.state == GameState.FLOP:
            break
        legal = game.betting_round.get_legal_actions(game.current_player, game.pot)
        game.perform_action(A.CHECK if A.CHECK in legal else A.CALL)
    else:
        pytest.fail("never reached the human's turn on the flop")
    state_before = snapshot(game)
    seen = {}

    def on_call(count):
        if count == 2:                      # the second prompt comes after the 'p'
            seen["after"] = snapshot(game)

    scripted(monkeypatch, ["p", "c"], on_call)
    game.human_turn()
    output = capsys.readouterr().out
    assert "YOUR PROBABILITIES" in output and "Win:" in output
    assert seen["after"] == state_before
