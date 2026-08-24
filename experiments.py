from mancala import Mancala
import ai
import heuristics
import time
import csv
import os


def choose_move(game, player, method="alpha_beta", depth=3, heuristic=heuristics.heuristic_1,
                 move_ordering=False, random_ties=False):
    moves = game.legal_moves(player)
    if not moves:
        return None

    if method == "random":
        import random
        return random.choice(moves)

    if method == "minimax":
        _, move = ai.minimax(game, depth, player, player, heuristic, move_ordering)
        return move

    if method == "alpha_beta":
        _, move = ai.minimax_alpha_beta(
            game, depth, float('-inf'), float('inf'), player, player,
            heuristic, move_ordering, random_ties)
        return move

    if method == "ids":
        _, move = ai.iterative_deepening(game, player, depth, heuristic, move_ordering)
        return move

    raise ValueError(f"Unknown method: {method}")


def play_game(p0={"method": "alpha_beta", "depth": 3, "heuristic": heuristics.heuristic_1,
                   "move_ordering": False, "random_ties": False},
              p1={"method": "alpha_beta", "depth": 3, "heuristic": heuristics.heuristic_1,
                   "move_ordering": False, "random_ties": False},
              verbose=False):
    game = Mancala()
    player = 0
    move_count = 0
    while not game.is_game_over():
        config = p0 if player == 0 else p1
        move = choose_move(game, player, **config)
        if move is None:
            break
        position, extra_turn, captured = game.make_move(player, move)
        move_count += 1
        if verbose:
            print(f"P{player} pit {move} -> last pos {position}, extra {extra_turn}, cap {captured} board {game.board}")
       
        if game.is_game_over():
            if verbose:
                print(f"Game ends after P{player} move: one side empty, remaining will be collected.")
            break
        if not extra_turn:
            player = 1 - player
    winner = game.get_winner()
    return winner, move_count, game.board.copy()


def tournament(p0, p1, games=100, alternate_first=True, verbose=False):
    p0_wins, p1_wins, draws = 0, 0, 0
    total_moves = 0
    for g in range(games):
        p0_first = (not alternate_first) or (g % 2 == 0)
        first = dict(p0) if p0_first else dict(p1)
        second = dict(p1) if p0_first else dict(p0)

        winner, moves, board = play_game(first, second, verbose=False)
        total_moves += moves

        winner_is_p0 = (winner == 0 and p0_first) or (winner == 1 and not p0_first)
        winner_is_p1 = (winner == 1 and p0_first) or (winner == 0 and not p0_first)

        if winner_is_p0:
            p0_wins += 1
        elif winner_is_p1:
            p1_wins += 1
        else:
            draws += 1
    avg_moves = total_moves / games if games else 0
    return p0_wins, p1_wins, draws, avg_moves


def compare_heuristics(games=100, depth=3, move_ordering=False, random_ties=True, verbose=True, save_csv=None):
    heuristics_list = [
        ("h1", heuristics.heuristic_1),
        ("h2", heuristics.heuristic_2),
        ("h3", heuristics.heuristic_3),
        ("h4", heuristics.heuristic_4),
        ("h5", heuristics.heuristic_5),
        ("h6", heuristics.heuristic_6),
    ]

    if verbose:
        print(f"========== HEURISTIC TOURNAMENT ==========")
        print(f"Games per unordered pair: {games}  |  Depth: {depth}  |  Move ordering: {move_ordering} | Random ties: {random_ties}")
        print()

    results = {}
    for name, _ in heuristics_list:
        results[name] = {}

    pairs = []
    for i in range(len(heuristics_list)):
        for j in range(i + 1, len(heuristics_list)):
            pairs.append((heuristics_list[i], heuristics_list[j]))

    pair_results = {}
    for (name_a, func_a), (name_b, func_b) in pairs:
        p0 = {"method": "alpha_beta", "depth": depth, "heuristic": func_a,
              "move_ordering": move_ordering, "random_ties": random_ties}
        p1 = {"method": "alpha_beta", "depth": depth, "heuristic": func_b,
              "move_ordering": move_ordering, "random_ties": random_ties}
        w_a, w_b, draws, avg_moves = tournament(p0, p1, games=games, alternate_first=True)
        pair_results[(name_a, name_b)] = (w_a, w_b, draws, avg_moves)
        results[name_a][name_b] = (w_a, w_b, draws, avg_moves)
        results[name_b][name_a] = (w_b, w_a, draws, avg_moves)
        if verbose:
            total = w_a + w_b + draws
            wr_a = w_a / total * 100 if total else 0
            wr_b = w_b / total * 100 if total else 0
            print(f"{name_a} vs {name_b}  ->  {name_a}: {w_a} ({wr_a:.1f}%) | {name_b}: {w_b} ({wr_b:.1f}%) | draws: {draws} | avg moves: {avg_moves:.1f}")

    if verbose:
        print()
        print("Summary matrix (wins for row vs column):")
        header = "      " + "".join(f"{n:>8}" for n, _ in heuristics_list)
        print(header)
        for name_a, _ in heuristics_list:
            row = f"{name_a:>4} "
            for name_b, _ in heuristics_list:
                if name_a == name_b:
                    row += f"{'-':>8}"
                else:
                    w_a, _, _, _ = results[name_a][name_b]
                    row += f"{w_a:>8}"
            print(row)
        print()

    total_wins = {name: 0 for name, _ in heuristics_list}
    total_losses = {name: 0 for name, _ in heuristics_list}
    total_draws = {name: 0 for name, _ in heuristics_list}
    for (name_a, name_b), (w_a, w_b, d, _) in pair_results.items():
        total_wins[name_a] += w_a
        total_losses[name_a] += w_b
        total_draws[name_a] += d
        total_wins[name_b] += w_b
        total_losses[name_b] += w_a
        total_draws[name_b] += d

    ranking = sorted(total_wins.items(), key=lambda kv: kv[1], reverse=True)
    if verbose:
        print("Overall ranking:")
        for name, wins in ranking:
            losses = total_losses[name]
            draws = total_draws[name]
            total = wins + losses + draws
            wr = wins / total * 100 if total else 0
            print(f"  {name}: wins={wins:3d}  losses={losses:3d}  draws={draws:3d}  win%={wr:.1f}%  (total {total} games)")
        print()
        best = ranking[0][0]
        print(f"BEST HEURISTIC (by total wins): {best}")
        print()

    if save_csv:
        os.makedirs(os.path.dirname(save_csv) or ".", exist_ok=True)
        with open(save_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["heuristic_a", "heuristic_b", "wins_a", "wins_b", "draws", "games", "win_pct_a", "win_pct_b", "avg_moves"])
            for (a, b), (w_a, w_b, d, am) in pair_results.items():
                total = w_a + w_b + d
                writer.writerow([a, b, w_a, w_b, d, total, w_a/total*100 if total else 0, w_b/total*100 if total else 0, f"{am:.2f}"])
            writer.writerow([])
            writer.writerow(["overall_rank", "heuristic", "wins", "losses", "draws", "win_pct"])
            for name, wins in ranking:
                losses = total_losses[name]
                draws = total_draws[name]
                tot = wins + losses + draws
                writer.writerow(["", name, wins, losses, draws, f"{wins/tot*100:.2f}" if tot else 0])

    return results, ranking, pair_results


def depth_experiment(heuristics_list=None, depths=range(1, 6), games=20, move_ordering=False):
    if heuristics_list is None:
        heuristics_list = [("h1", heuristics.heuristic_1)]
    print("========== DEPTH VARIATION EXPERIMENT ==========")
    print(f"Games per depth pair: {games}")
    for name, func in heuristics_list:
        print(f"\nHeuristic {name}:")
        for d in depths:
            g = Mancala()
            ai.nodes_searched = 0
            _, _ = ai.minimax_alpha_beta(g, d, float('-inf'), float('inf'), 0, 0, func, move_ordering=False)
            nodes_no_order = ai.nodes_searched
            ai.nodes_searched = 0
            _, _ = ai.minimax_alpha_beta(g, d, float('-inf'), float('inf'), 0, 0, func, move_ordering=True)
            nodes_order = ai.nodes_searched
            print(f"  depth={d}: nodes no-order={nodes_no_order:5d}  ordered={nodes_order:5d}  reduction={(1-nodes_order/nodes_no_order)*100 if nodes_no_order else 0:5.1f}%")

    print("\n-- Depth advantage: h1 depth=2 vs depth=4 --")
    base_heuristic = heuristics.heuristic_1
    d_low, d_high = 2, 4
    p_low = {"method": "alpha_beta", "depth": d_low, "heuristic": base_heuristic,
             "move_ordering": True, "random_ties": True}
    p_high = {"method": "alpha_beta", "depth": d_high, "heuristic": base_heuristic,
              "move_ordering": True, "random_ties": True}
    w_low, w_high, draws, avg = tournament(p_low, p_high, games=games, alternate_first=True)
    print(f"  h1 d={d_low} vs h1 d={d_high} -> d{d_low}:{w_low} | d{d_high}:{w_high} | draws:{draws} | avg_moves:{avg:.1f}")


def move_ordering_ablation_experiment(depths=range(1, 7), heuristic=heuristics.heuristic_1):
    print("========== MOVE ORDERING ABLATION (alpha-beta) ==========")
    print(f"Heuristic: {heuristic.__name__}")
    print(f"{'depth':>5} | {'no-order nodes':>14} | {'ordered nodes':>13} | {'reduction':>9} | {'move plain':>10} | {'move ord':>8}")
    print("-" * 75)
    for depth in depths:
        g = Mancala()
        ai.nodes_searched = 0
        _, m1 = ai.minimax_alpha_beta(g, depth, float('-inf'), float('inf'), 0, 0, heuristic, move_ordering=False)
        n_no = ai.nodes_searched
        ai.nodes_searched = 0
        _, m2 = ai.minimax_alpha_beta(g, depth, float('-inf'), float('inf'), 0, 0, heuristic, move_ordering=True)
        n_yes = ai.nodes_searched
        red = (1 - n_yes / n_no) * 100 if n_no else 0
        print(f"{depth:5d} | {n_no:14d} | {n_yes:13d} | {red:8.1f}% | {str(m1):>10} | {str(m2):>8}")


def iterative_vs_alphabeta_experiment(max_depth=4, heuristic=heuristics.heuristic_1, move_ordering=False):
    print("========== ITERATIVE DEEPENING vs ALPHA-BETA ==========")
    g = Mancala()
    for d in range(1, max_depth + 1):
        ai.nodes_searched = 0
        start = time.time()
        v1, m1 = ai.minimax_alpha_beta(g, d, float('-inf'), float('inf'), 0, 0, heuristic, move_ordering=move_ordering)
        t1 = time.time() - start
        n1 = ai.nodes_searched

        ai.nodes_searched = 0
        start = time.time()
        v2, m2 = ai.iterative_deepening(g, 0, d, heuristic, move_ordering=move_ordering)
        t2 = time.time() - start
        n2 = ai.nodes_searched

        print(f"depth {d}: AB  move={m1} eval={v1} nodes={n1:5d} time={t1*1000:.1f}ms | IDS move={m2} eval={v2} nodes={n2:5d} time={t2*1000:.1f}ms | same_move={'YES' if m1==m2 else 'NO'}")


def timing_experiment(depth=4, heuristic=heuristics.heuristic_1):
    print("========== TIMING / NODES ==========")
    g = Mancala()
    for method, mo in [("minimax", False), ("alpha_beta_no_order", False), ("alpha_beta_order", True)]:
        ai.nodes_searched = 0
        start = time.time()
        if method == "minimax":
            v, m = ai.minimax(g, depth, 0, 0, heuristic, move_ordering=False)
        else:
            v, m = ai.minimax_alpha_beta(g, depth, float('-inf'), float('inf'), 0, 0, heuristic, move_ordering=(mo == True))
        elapsed = time.time() - start
        print(f"{method:20s} depth={depth} move={m} eval={v} nodes={ai.nodes_searched:5d} time={elapsed*1000:.2f}ms")