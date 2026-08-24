from heuristics import heuristic_1
import random

nodes_searched = 0

def score_move(game, player, move, heuristic, perspective=None):
    """Evaluate child after move from perspective player's view.
    If perspective is None, evaluates from mover's view (player)."""
    g2 = game.copy()
    g2.make_move(player, move)
    eval_player = perspective if perspective is not None else player
    return heuristic(g2, eval_player)

def ordered_moves(game, player, heuristic, ai_player=None, descending=True):
    """
    Return moves sorted by heuristic value.
    - If ai_player is given, scoring is from ai_player perspective:
        * maximizing player (player==ai_player) -> descending=True (high eval first)
        * minimizing player -> descending=False (low eval first)
    - If ai_player is None, scoring from mover perspective and always descending=True
      (best for mover first)
    """
    scored = []
    if ai_player is not None:
        for move in game.legal_moves(player):
            val = score_move(game, player, move, heuristic, perspective=ai_player)
            scored.append((move, val))
        scored.sort(key=lambda m: m[1], reverse=descending)
    else:
        for move in game.legal_moves(player):
            val = score_move(game, player, move, heuristic, perspective=player)
            scored.append((move, val))
        scored.sort(key=lambda m: m[1], reverse=True)
    return [m[0] for m in scored]

def move_list(game, player, heuristic, use_ordering, ai_player=None, descending=True):
    if use_ordering:
        return ordered_moves(game, player, heuristic, ai_player=ai_player, descending=descending)
    return game.legal_moves(player)

def terminal_value(game, ai_player, heuristic):
    #Evaluate board. If game over, collect remaining stones first
    if game.is_game_over():
        tmp = game.copy()
        tmp.collect_remaining_stones()
        return heuristic(tmp, ai_player)
    return heuristic(game, ai_player)

def minimax(game, depth, ai_player, maximizing_player, heuristic=heuristic_1, move_ordering=False):
    global nodes_searched
    nodes_searched += 1
    
    if depth == 0 or game.is_game_over():
        return terminal_value(game, ai_player, heuristic), None
        
    # ordering: if move_ordering, order by heuristic from ai perspective
    legal_moves = move_list(game, maximizing_player, heuristic, move_ordering,
                            ai_player=ai_player,
                            descending=(maximizing_player == ai_player))
        
    if not legal_moves:
        return terminal_value(game, ai_player, heuristic), None
    
    if maximizing_player == ai_player:
        best_value = float('-inf')
        best_move = None
        
        for move in legal_moves:
            new_game = game.copy()
            position, extra_turn, captured = new_game.make_move(maximizing_player, move)
            
            if extra_turn:
                next_player = maximizing_player
            else:
                next_player = 1 - maximizing_player
            value, _ = minimax(new_game, depth - 1, ai_player, next_player, heuristic, move_ordering)
            
            if value > best_value:
                best_value = value
                best_move = move
            
        return best_value, best_move
    else:
        best_value = float('inf')
        best_move = None
        
        for move in legal_moves:
            new_game = game.copy()
            position, extra_turn, captured = new_game.make_move(maximizing_player, move)
            
            if extra_turn:
                next_player = maximizing_player
            else:
                next_player = 1 - maximizing_player
            value, _ = minimax(new_game, depth - 1, ai_player, next_player, heuristic, move_ordering)
            
            if value < best_value:
                best_value = value
                best_move = move
            
        return best_value, best_move

def minimax_alpha_beta(game, depth, alpha, beta, player, ai_player, heuristic=heuristic_1, move_ordering=False, random_ties=False):
    
    global nodes_searched
    nodes_searched += 1
    
    if depth == 0 or game.is_game_over():
        return terminal_value(game, ai_player, heuristic), None
    
    legal_moves = move_list(game, player, heuristic, move_ordering,
                            ai_player=ai_player,
                            descending=(player == ai_player))
    
    if not legal_moves:
        return terminal_value(game, ai_player, heuristic), None
    
    if player == ai_player:
        best_value = float('-inf')
        best_moves = []
        
        for move in legal_moves:
            new_game = game.copy()
            position, extra_turn, captured = new_game.make_move(player, move)
            
            if extra_turn:
                next_player = player
            else:
                next_player = 1 - player
            
            value, _ = minimax_alpha_beta(new_game, depth - 1, alpha, beta, next_player, ai_player, heuristic, move_ordering, random_ties)
            if value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
            
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        best_move = random.choice(best_moves) if random_ties and best_moves else (best_moves[0] if best_moves else None)
        return best_value, best_move
    
    else:
        best_value = float('inf')
        best_moves = []
        
        for move in legal_moves:
            new_game = game.copy()
            position, extra_turn, captured = new_game.make_move(player, move)
            
            if extra_turn:
                next_player = player
            else:
                next_player = 1 - player
            
            value, _ = minimax_alpha_beta(new_game, depth - 1, alpha, beta, next_player, ai_player, heuristic, move_ordering, random_ties)
            if value < best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
            
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        best_move = random.choice(best_moves) if random_ties and best_moves else (best_moves[0] if best_moves else None)
        return best_value, best_move

def iterative_deepening(game, ai_player, max_depth, heuristic=heuristic_1, move_ordering=False):
    best_value, best_move = None, None
    
    for d in range(1, max_depth + 1):
        if move_ordering and best_move is not None:
            # order root moves with previous best first, then heuristic ordering
            ordered = ordered_moves(game, ai_player, heuristic, ai_player=ai_player, descending=True)
            if best_move in ordered:
                ordered.remove(best_move)
                ordered.insert(0, best_move)
            value, move = ids_search(game, d, ai_player, ai_player, heuristic, ordered, move_ordering)
        else:
            value, move = ids_search(game, d, ai_player, ai_player, heuristic, None, move_ordering)
        best_value, best_move = value, move
    return best_value, best_move

def ids_search(game, depth, ai_player, player, heuristic, first_moves, move_ordering=False):
    global nodes_searched
    nodes_searched += 1
    
    if depth == 0 or game.is_game_over():
        return terminal_value(game, ai_player, heuristic), None
    
    # Determine move list: root may have pre-ordered first_moves
    if first_moves is not None:
        legal_moves = first_moves
    else:
        if move_ordering:
            legal_moves = ordered_moves(game, player, heuristic, ai_player=ai_player, descending=(player==ai_player))
        else:
            legal_moves = game.legal_moves(player)

    if not legal_moves:
        return terminal_value(game, ai_player, heuristic), None
    
    if player == ai_player:
        best_value = float('-inf')
        best_move = None
        for move in legal_moves:
            new_game = game.copy()
            new_game.make_move(player, move)
            nxt = player if new_game.last_extra_turn else 1 - player
            value, _ = ids_search(new_game, depth - 1, ai_player, nxt, heuristic, None, move_ordering)
            if value > best_value:
                best_value, best_move = value, move
        return best_value, best_move
    else:
        best_value = float('inf')
        best_move = None
        for move in legal_moves:
            new_game = game.copy()
            new_game.make_move(player, move)
            nxt = player if new_game.last_extra_turn else 1 - player
            value, _ = ids_search(new_game, depth - 1, ai_player, nxt, heuristic, None, move_ordering)
            if value < best_value:
                best_value, best_move = value, move
        return best_value, best_move
