#track player statistics
# reference- https://github.com/techwithtim/Online-Python-Game
class Database:
    
    def __init__(self):
        self.players = {}  # Dictionary that will store player stats
        
    # adding a player
    def add_player(self, username):
        if username not in self.players:
            self.players[username] = {
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
     
    # Updating status such as win, lose and draw       
    def update_stats(self, username, result):
        if username not in self.players:
            self.add_player(username)
            
        if result == "win":
            self.players[username]["wins"] += 1
        elif result == "loss":
            self.players[username]["losses"] += 1
        elif result == "draw":
            self.players[username]["draws"] += 1
    
    # getting the game statistics if it exists in the database
    def get_stats(self, username):
        if username not in self.players:
            return None
        return self.players[username]