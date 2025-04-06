# reference- https://github.com/techwithtim/Online-Python-Game

class Room:
    # initializing process
    def __init__(self, player1, player2):
        self.play_board = [' '] * 9
        self.players = {player1: 'O', player2: 'X'}  # X would go first
        self.curr_player = player2
        self.finished = False
        
    # recording the moves made by the players
    def make_move(self, client, position):
        # Check if it's the current player's turn
        if client != self.curr_player or self.finished:
            return False
            
        # is the move valid
        position = int(position)  # Ensure it's an integer
        if position < 0 or position > 8 or self.play_board[position] != ' ':
            return False
            
        # Make move
        self.play_board[position] = self.players[client]
        
        # Check win or draw
        winner = self.check_winner()
        if winner:
            self.finished = True
            return 'win'
        elif ' ' not in self.play_board:
            self.finished = True
            return 'draw'
            
        # turns switching
        for player in self.players:
            if player != client:
                self.curr_player = player
                break
                
        return True
    
    # checking for the winner, these lines of code would be printed in the command prompt
    def check_winner(self):
        # Check win conditions
        wining_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for line in wining_lines:
            a, b, c = line
            if self.play_board[a] != ' ' and self.play_board[a] == self.play_board[b] == self.play_board[c]:
                return self.players[self.curr_player]
        
        return None
