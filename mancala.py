import random

class Mancala:
    def __init__(self):
        self.board = [
            4,4,4,4,4,4,
            0,
            4,4,4,4,4,4,
            0
        ]
        self.current_player=0
        self.last_player=None
        self.last_extra_turn=0
        self.last_captured=0
    
    def get_pits(self,player):
        if player == 0:
            return range(0, 6)
        else:
            return range(7, 13)
    
    def get_store(self,player):
        if player == 0:
            return 6
        else:
            return 13
    
    def legal_moves(self, player):
        moves = []
        
        for pit in self.get_pits(player):
            if self.board[pit] > 0:
                moves.append(pit)
        
        return moves
    
    def make_move(self,player,pit):
        stones=self.board[pit]
        
        self.board[pit]=0
        
        position=pit
        
        while stones>0:
            position=(position+1)%14
            
            if position==self.get_store(1-player):
                continue
            
            self.board[position]+=1
            stones-=1
        
        captured=0
        
        my_pits=self.get_pits(player)
        
        if position in my_pits and self.board[position]==1:
            opposite=12-position
            
            if self.board[opposite]>0:
                captured=self.board[opposite]+1
                self.board[self.get_store(player)]+=captured
                self.board[position]=0
                self.board[opposite]=0
        
        extra_turn=(position==self.get_store(player))
        
        self.last_player=player
        self.last_extra_turn=extra_turn
        self.last_captured=captured
        
        return position,extra_turn,captured
    
    def is_game_over(self):
        p0_empty=all(self.board[pit]==0 for pit in self.get_pits(0))
        p1_empty=all(self.board[pit]==0 for pit in self.get_pits(1))
        
        return p0_empty or p1_empty
    
    def collect_remaining_stones(self):
        for player in [0, 1]:
            total=0
            
            for pit in self.get_pits(player):
                total+=self.board[pit]
                self.board[pit]=0
            
            self.board[self.get_store(player)]+=total
    
    def get_winner(self):
        if not self.is_game_over():
            return None
        
        self.collect_remaining_stones()
        
        if self.board[self.get_store(0)] > self.board[self.get_store(1)]:
            return 0
        elif self.board[self.get_store(1)] > self.board[self.get_store(0)]:
            return 1
        else:
            return -1 
    
    def copy(self):
        new_game = Mancala()
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.last_player = self.last_player
        new_game.last_extra_turn = self.last_extra_turn
        new_game.last_captured = self.last_captured
        return new_game
    
    def random_move(self, player):
        moves = self.legal_moves(player)

        if not moves:
            return None

        return random.choice(moves)
    
    def play_random_game(self):

        player = 0

        while not self.is_game_over():

            moves = self.legal_moves(player)

            if not moves:
                break

            pit = random.choice(moves)

            print(f"Player {player} chooses pit {pit}")

            position, extra_turn, captured = self.make_move(player, pit)

            print("Board:", self.board)
            print("Last position:", position)
            print("Extra turn:", extra_turn)
            print("Captured:", captured)
            print()

            # Keep the same player if they earned an extra turn
            if not extra_turn:
                player = 1 - player

        # Finish the game
        winner = self.get_winner()

        print("========== GAME OVER ==========")
        print("Final board:", self.board)

        if winner == -1:
            print("Result: Draw")
        else:
            print(f"Winner: Player {winner}")