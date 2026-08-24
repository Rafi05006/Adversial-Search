TOTAL_STONES = 48


def side_stones(game, player):
    return sum(game.board[p] for p in game.get_pits(player))


def sow_last_position(game, player, pit):
    """Where the last sown stone from `pit` lands, skipping the opponent's store."""
    n = game.board[pit]
    if n == 0:
        return None
    pos = pit
    opp_store = game.get_store(1 - player)
    for _ in range(n):
        pos = (pos + 1) % 14
        if pos == opp_store:
            pos = (pos + 1) % 14
    return pos


def sow_lands_on(game, player, pit):
    """True if sowing `pit` ends on the player's own side (pits or store)."""
    last_pos = sow_last_position(game, player, pit)
    if last_pos is None:
        return False
    region = list(game.get_pits(player)) + [game.get_store(player)]
    return last_pos in region


def heuristic_1(game, player):
    my_store = game.get_store(player)
    opponent_store = game.get_store(1 - player)
    return game.board[my_store] - game.board[opponent_store]


def heuristic_2(game, player, W1=1.0, W2=0.1):
    my_store = game.board[game.get_store(player)]
    opp_store = game.board[game.get_store(1 - player)]
    my_side = side_stones(game, player)
    opp_side = side_stones(game, 1 - player)
    return W1 * (my_store - opp_store) + W2 * (my_side - opp_side)


def heuristic_3(game, player, W1=1.0, W2=0.1, W3=1.0):
    base = heuristic_2(game, player, W1, W2)
    extra_turn = 1 if (game.last_player == player and game.last_extra_turn) else 0
    return base + W3 * extra_turn


def heuristic_4(game, player, W1=1.0, W2=0.1, W3=1.0, W4=0.25):
    base = heuristic_3(game, player, W1, W2, W3)
    captured = game.last_captured if game.last_player == player else 0
    return base + W4 * captured


def heuristic_5(game, player, W1=1.0, W2=0.1, W3=0.5, W4=0.1):
    """Store/side diff plus look-ahead extra-move and capture potential."""
    my_pits = list(game.get_pits(player))
    my_store = game.get_store(player)

    extra_chances = 0
    for pit in my_pits:
        if game.board[pit] == 0:
            continue
        if sow_last_position(game, player, pit) == my_store:
            extra_chances += 1

    capture_opts = 0
    for pit in my_pits:
        if game.board[pit] == 0:
            continue
        last_pos = sow_last_position(game, player, pit)
        if last_pos in my_pits and game.board[last_pos] == 0:
            opposite = 12 - last_pos
            if game.board[opposite] > 0:
                capture_opts += game.board[opposite] + 1

    return heuristic_2(game, player, W1, W2) + W3 * extra_chances + W4 * capture_opts


def heuristic_6(game, player, W_store=1.0, W_side=0.1, W_win=2.0, W_near=1.0,
                W_furthest=0.5, W_extra=1.0, W_capture=1.0):
    """Comprehensive heuristic covering all eleven strategic factors."""
    my_store = game.get_store(player)
    opp_store = game.get_store(1 - player)
    my_pits = list(game.get_pits(player))
    opp_pits = list(game.get_pits(1 - player))

    store_diff = game.board[my_store] - game.board[opp_store]

    my_side = side_stones(game, player)
    opp_side = side_stones(game, 1 - player)
    side_diff = my_side - opp_side

    half = TOTAL_STONES // 2
    my_win = min(game.board[my_store] / half, 1.0)
    opp_win = min(game.board[opp_store] / half, 1.0)
    win_diff = my_win - opp_win

    my_near = sum(game.board[p] for p in my_pits if sow_lands_on(game, player, p))
    opp_near = sum(game.board[p] for p in opp_pits if sow_lands_on(game, 1 - player, p))
    near_diff = my_near - opp_near

    my_valid = [p for p in my_pits if game.board[p] > 0]
    if my_valid:
        furthest_bonus = max(my_store - p for p in my_valid if my_store - p > 0)
    else:
        furthest_bonus = 0

    extra_turn = 1 if (game.last_player == player and game.last_extra_turn) else 0
    captured = game.last_captured if game.last_player == player else 0

    return (W_store * store_diff
            + W_side * side_diff
            + W_win * win_diff
            + W_near * near_diff
            + W_furthest * furthest_bonus
            + W_extra * extra_turn
            + W_capture * captured)