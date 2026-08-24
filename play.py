import sys
import heuristics
import ai
from mancala import Mancala

HEURISTICS = {
    "1": ("heuristic_1 (store difference)", heuristics.heuristic_1),
    "2": ("heuristic_2 (store + side)", heuristics.heuristic_2),
    "3": ("heuristic_3 (+ extra move)", heuristics.heuristic_3),
    "4": ("heuristic_4 (+ capture)", heuristics.heuristic_4),
    "5": ("heuristic_5 (look-ahead potential) - recommended", heuristics.heuristic_5),
    "6": ("heuristic_6 (comprehensive)", heuristics.heuristic_6),
}


def ask(prompt, valid, default=None):
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            raise
        if raw == "" and default is not None:
            return default
        if raw in valid:
            return raw
        print(f"  Please enter one of: {', '.join(sorted(valid))}" + (f" (or Enter for default {default})" if default else ""))


def choose_settings():
    print("=" * 60)
    print("MANCALA - PLAYER vs AI")
    print("=" * 60)
    print("Board: 6 pits per side (0-5 for P0, 7-12 for P1), stores 6 (P0) and 13 (P1).")
    print()

    side = ask("Play as Player 0 (moves first) or Player 1? [0/1] (default 0): ",
               {"0", "1"}, default="0")
    human_player = int(side)
    ai_player = 1 - human_player

    print("\nChoose the AI's heuristic:")
    for key, (label, _) in HEURISTICS.items():
        print(f"  {key}: {label}")
    h_choice = ask("Heuristic [1-6] (default 5): ", set(HEURISTICS.keys()), default="5")
    heuristic_name, heuristic_func = HEURISTICS[h_choice]

    depth = ask("AI search depth [1-8] (default 5): ",
                {str(d) for d in range(1, 9)}, default="5")
    depth = int(depth)
    if depth >= 6:
        print(f"  Note: depth {depth} may be slow (exponential).")
        print(f"        Approx nodes: depth5~287-1042, depth6~794-3786 (ordered vs no-order).")
        if depth >= 7:
            print(f"        Depth 7-8 can take seconds per move.")
    if depth <= 2:
        print(f"  Note: depth {depth} is very shallow, AI will be weak.")

    print(f"\nYou are Player {human_player} {'(P0, bottom row 0-5)' if human_player==0 else '(P1, top row 7-12)'}")
    print(f"AI is Player {ai_player}, using {heuristic_name} at depth {depth}.")
    print(f"Player 0 moves first.\n")
    return human_player, ai_player, heuristic_func, depth


def human_move(game, player):
    legal = game.legal_moves(player)
    # Clarify which pits belong to human
    if player == 0:
        print(f"Your pits are 0-5 (bottom row). Your legal pits: {legal}")
    else:
        print(f"Your pits are 7-12 (top row, reversed 12..7). Your legal pits: {legal}")
    print("Type pit number and press Enter. (Ctrl+C to quit)")
    while True:
        try:
            raw = input("Choose a pit to sow from: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nMove cancelled by user.")
            raise
        if raw.lower() in ("q", "quit", "exit"):
            print("Quitting game.")
            raise KeyboardInterrupt
        if raw.isdigit() and int(raw) in legal:
            return int(raw)
        print(f"  Invalid choice. Pick one of: {legal}")


def ai_move(game, player, heuristic, depth):
    print("AI is thinking...")
    try:
        _, move = ai.minimax_alpha_beta(
            game, depth, float('-inf'), float('inf'), player, player,
            heuristic, move_ordering=True, random_ties=True)
    except Exception as e:
        print(f"AI search failed: {e}")
        # fallback to random
        move = game.random_move(player)
        print(f"Fallback random move: {move}")
    if move is None:
        print("AI has no legal moves.")
        return None
    print(f"AI plays pit {move}")
    return move


def play():
    try:
        human_player, ai_player, heuristic, depth = choose_settings()
    except (KeyboardInterrupt, EOFError):
        print("\nSetup cancelled. Exiting.")
        return

    game = Mancala()
    player = 0  # P0 always starts per Mancala rules

    print("\nInitial board:")
    game.display(perspective=player)
    print(f"Player {player} starts.")
    print()

    try:
        while not game.is_game_over():
            if not game.legal_moves(player):
                print(f"Player {player} has no moves. Game ends.")
                break

            # Show whose turn
            if player == human_player:
                print(f"--- Your turn (Player {player}) ---")
                try:
                    move = human_move(game, player)
                except (KeyboardInterrupt, EOFError):
                    print("\nGame aborted by user.")
                    return
            else:
                print(f"--- AI turn (Player {player}) ---")
                try:
                    move = ai_move(game, player, heuristic, depth)
                except (KeyboardInterrupt, EOFError):
                    print("\nAI move interrupted.")
                    return
                if move is None:
                    break

            # Execute move (validated in mancala.py)
            try:
                position, extra_turn, captured = game.make_move(player, move)
            except ValueError as e:
                print(f"Illegal move: {e}")
                continue

            is_over = game.is_game_over()
            game.display(perspective=player if extra_turn and not is_over else 1-player if not is_over else None)

            if captured:
                who = "You" if player == human_player else "AI"
                print(f"{who} captured {captured} stones!")
            if is_over:
                # Game ends immediately - do not grant extra turn, break to final collection
                print("Game ends: one side has no stones. Remaining stones will be collected into the store of the player who still has stones.")
                break
            if extra_turn:
                who = "You get" if player == human_player else "AI gets"
                print(f"{who} an extra turn! (last stone landed in store)")
                # same player repeats, don't switch
            else:
                player = 1 - player

        # Game over - collect and display final
        winner = game.get_winner()
        print("\n")
        game.display()
        print("=" * 60)
        if winner == -1:
            print("GAME OVER - It's a draw!")
        elif winner == human_player:
            print("GAME OVER - You win!")
        else:
            print("GAME OVER - AI wins!")
        print(f"Final score - You (P{human_player}): {game.board[game.get_store(human_player)]}  "
              f"AI (P{ai_player}): {game.board[game.get_store(ai_player)]}")
        print(f"Total stones: {game.board[game.get_store(0)] + game.board[game.get_store(1)]} / 48")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nGame interrupted. Final board:")
        game.display()
        try:
            # Show current scores without collecting (game may not be over)
            print(f"Current stores - P0: {game.board[game.get_store(0)]}  P1: {game.board[game.get_store(1)]}")
        except:
            pass
        print("Thanks for playing!")


if __name__ == "__main__":
    play()
