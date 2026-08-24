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
        # Validate pit
        if pit not in self.get_pits(player):
            raise ValueError(f"Pit {pit} not owned by player {player}")
        if self.board[pit] == 0:
            raise ValueError(f"Pit {pit} is empty")
        
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
        
        # Capture: last stone lands in empty own pit and opposite has stones
     
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
        
        #End-game sweep: when one side is empty, the other side sweeps
        #remaining stones into their store. Since empty side has 0,
       
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
    def display(self, perspective=None):
        """
        Display the Mancala board with fixed-width alignment.

        perspective=None:
            Show the complete board.

        perspective=0/1:
            Also show that player's legal moves.
        """

        # -----------------------------
        # Pit ordering
        # -----------------------------
        p1_pits = list(self.get_pits(1))[::-1]   # 12 -> 7
        p0_pits = list(self.get_pits(0))         # 0 -> 5

        # -----------------------------
        # Get values
        # -----------------------------
        store1 = self.board[self.get_store(1)]
        store0 = self.board[self.get_store(0)]

        p1_values = [self.board[p] for p in p1_pits]
        p0_values = [self.board[p] for p in p0_pits]

        # -----------------------------
        # Fixed-width pit cells
        # Each pit occupies EXACTLY 4 characters
        # -----------------------------
        CELL_WIDTH = 4

        p1_cells = [f"{x:>{CELL_WIDTH}}" for x in p1_values]
        p0_cells = [f"{x:>{CELL_WIDTH}}" for x in p0_values]

        p1_row = "".join(p1_cells)
        p0_row = "".join(p0_cells)

        # Width of the complete pit area
        PIT_WIDTH = CELL_WIDTH * len(p1_pits)

        # Store width
        STORE_WIDTH = 9

        # Complete board width:
        #
        # [P1 Store] [pits] [separator]
        # [padding]   [pits] [P0 Store]
        #
        BOARD_WIDTH = STORE_WIDTH + 3 + PIT_WIDTH + 3 + STORE_WIDTH

        # -----------------------------
        # Heading
        # -----------------------------
        print()
        print("Mancala Board".center(BOARD_WIDTH))

        # -----------------------------
        # Top pit labels
        # -----------------------------
        label_p1 = "P1 pits (12 -> 7)"
        print(label_p1.center(BOARD_WIDTH))

        print(
            (" " * (STORE_WIDTH + 3)) +
            p1_row +
            (" " * (STORE_WIDTH + 3))+
            "\n"
        )

        # -----------------------------
        # Main board
        # -----------------------------

        # Top side:
        # P1 store | P1 pits | P0 store area
        top_line = (
            f"{'P1 Store':<{STORE_WIDTH}}"
            f" |"
            f"{p1_row}"
            f"|"
            f"{'':>{STORE_WIDTH}}"
        )

        # Bottom side:
        # P1 store area | P0 pits | P0 store
        bottom_line = (
            f"{'':<{STORE_WIDTH}}"
            f"  |"
            f"{p0_row}"
            f"| "
            f"{'P0 Store':<{STORE_WIDTH - 1}}{store0:2}"
        )

        # Insert actual P1 store value
        top_line = (
            f"{'P1 Store':<8}{store1:2}"
            f" |"
            f"{p1_row}"
            f"|"
            f"{'':>{STORE_WIDTH}}"
        )

        print(top_line)
        print(bottom_line+"\n")

        # -----------------------------
        # Bottom pit heading
        # -----------------------------
        label_p0 = "P0 pits (0 -> 5)"
        print(label_p0.center(BOARD_WIDTH))

        # -----------------------------
        # Pit numbers
        # -----------------------------
        p0_numbers = "".join(
            f"{p:>{CELL_WIDTH}}" for p in p0_pits
        )

        p1_numbers = "".join(
            f"{p:>{CELL_WIDTH}}" for p in p1_pits
        )

        
        print(
            (" " * (STORE_WIDTH + 3)) +
            p1_numbers +
            (" " * 3) +
            "<- P1 pit numbers (reversed)"
        )
        
        print(
            (" " * (STORE_WIDTH + 3)) +
            p0_numbers +
            (" " * 3) +
            "<- P0 pit numbers"
        )


        # -----------------------------
        # Legal moves
        # -----------------------------
        if perspective is not None:
            legal = self.legal_moves(perspective)
            print()
            print(f"Player {perspective} legal moves: {legal}")

        print()
    def __str__(self):
        return f"Mancala(board={self.board}, last_player={self.last_player})"

    def __repr__(self):
        return self.__str__()

    def random_move(self, player):
        moves = self.legal_moves(player)

        if not moves:
            return None

        return random.choice(moves)
    