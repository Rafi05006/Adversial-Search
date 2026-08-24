import inspect
import sys
import os
from datetime import datetime

import mancala
import ai
import heuristics
import experiments

DEPTH = 3
AI_PLAYER = 0

QUICK_MODE = False
TOURNAMENT_GAMES = 10 if QUICK_MODE else 100
DEPTH_ADVANTAGE_GAMES = 6 if QUICK_MODE else 20


def all_heuristics():
    funcs = []
    for name, func in inspect.getmembers(heuristics, inspect.isfunction):
        if name.startswith("heuristic_"):
            funcs.append((name, func))
    return sorted(funcs)


def run_pairs():
    print("========== HEURISTIC COMPARISON (single state, depth={}) ==========".format(DEPTH))
    print(f"Depth: {DEPTH}  |  AI Player: {AI_PLAYER}")
    print(f"Board start: {mancala.Mancala().board}")
    print()
    print(f"{'heuristic':<12} | {'minimax move':>12} | {'eval':>8} | {'nodes':>6} || {'AB move':>7} | {'eval':>8} | {'nodes':>6} | {'reduction':>9} | match")
    print("-"*110)
    for name, h in all_heuristics():
        game = mancala.Mancala()

        ai.nodes_searched = 0
        v1, m1 = ai.minimax(game, DEPTH, AI_PLAYER, AI_PLAYER, h)
        n1 = ai.nodes_searched

        ai.nodes_searched = 0
        v2, m2 = ai.minimax_alpha_beta(
            game, DEPTH, float('-inf'), float('inf'), AI_PLAYER, AI_PLAYER, h)
        n2 = ai.nodes_searched

        same = "OK" if (m1 == m2 and v1 == v2) else "DIFF"
        reduction = (1 - n2/n1)*100 if n1 else 0
        print(f"{name:<12} | {str(m1):>12} | {str(v1):>8} | {n1:>6} || {str(m2):>7} | {str(v2):>8} | {n2:>6} | {reduction:8.1f}% | {same}")
    print()


def move_ordering_ablation():
    print("========== MOVE ORDERING ABLATION (alpha-beta, heuristic_1) ==========")
    print(f"Heuristic: heuristic_1 (store diff) | Player: {AI_PLAYER}")
    print()
    experiments.move_ordering_ablation_experiment(depths=range(1, 7), heuristic=heuristics.heuristic_1)
    print()


def iterative_deepening_demo():
    print("========== ITERATIVE DEEPENING (heuristic_1) ==========")
    print()
    experiments.iterative_vs_alphabeta_experiment(max_depth=4, heuristic=heuristics.heuristic_1, move_ordering=False)
    print()


def depth_variation_experiment():
    print("========== DEPTH LIMIT VARIATION ==========")
    print()
    experiments.depth_experiment(depths=range(1, 6), games=DEPTH_ADVANTAGE_GAMES, move_ordering=True)
    print()


def main():
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_path = "results/experiment_output.txt"
    csv_path = "results/tournament_results.csv"

    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    log_file = open(output_path, "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log_file)

    try:
        print("="*90)
        print("ADVERSARIAL SEARCH - MANCALA - Assignment 3 Experiment Report")
        print("="*90)
        print(f"Generated: {timestamp}")
        print(f"Platform: Mancala 6 pits per side, 4 stones each, 48 total")
        print(f"Algorithms: Minimax, Alpha-Beta Pruning, Iterative Deepening, Move Ordering")
        print(f"Heuristics: h1..h4 per spec + h5, h6 (own heuristics)")
        print(f"Default Depth: {DEPTH} | Games per pair: {TOURNAMENT_GAMES} | Mode: {'QUICK' if QUICK_MODE else 'FULL'}")
        print("="*90)
        print()

        run_pairs()
        move_ordering_ablation()
        iterative_deepening_demo()

        print("="*90)
        print(f"EXPERIMENT 4: HEURISTIC TOURNAMENT - {TOURNAMENT_GAMES} GAMES PER PAIR")
        print("="*90)
        print(f"Method: Alpha-Beta, Depth={DEPTH}, move ordering on, alternate first mover, random ties enabled")
        print()
        experiments.compare_heuristics(games=TOURNAMENT_GAMES, depth=DEPTH, move_ordering=True,
                                        random_ties=True, save_csv=csv_path)
        print()

        depth_variation_experiment()

        print("="*90)
        print("EXPERIMENT 6: TIMING / SEARCH EFFICIENCY")
        print("="*90)
        experiments.timing_experiment(depth=4, heuristic=heuristics.heuristic_1)
        print()
        experiments.timing_experiment(depth=4, heuristic=heuristics.heuristic_4)
        print()

        print("="*90)
        print(f"Output saved to: {output_path}")
        print(f"CSV saved to: {csv_path}")
        print("="*90)

    finally:
        sys.stdout = original_stdout
        log_file.close()
        print(f"\n[Done] Output written to {output_path}")


if __name__ == "__main__":
    main()