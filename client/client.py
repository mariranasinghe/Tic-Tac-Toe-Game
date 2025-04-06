import socket
import threading
import json
from protocols import Protocols

# reference- https://github.com/techwithtim/Online-Python-Game
class Client:
    # setting up the connection similar to the server's main.py file
    def __init__(self, host="127.0.0.1", port=55555):
        self.nickname = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.server.connect((host, port))
            print("Connected to server")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.server = None
            return
            
        self.closed = False
        self.started = False
        self.play_board = [' '] * 9
        self.player_symbol = None
        self.current_turn = False
        self.opponent_name = None
        self.winner = None
        self.waiting_for_player = True
    
    # thread to receive messages
    def start(self):
        if not self.server:
            print("Cannot start: No server connection")
            return
            
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.daemon = True  # When the main thread exits, make the thread exit
        receive_thread.start()
        
    # Helps in message sending 
    def send(self, request, message):
        data = {"type": request, "data": message}
        json_string = json.dumps(data) + "\n"
        self.server.send(json_string.encode("ascii"))

    # Processing messages
    def receive(self):
        buffer = ""
        while not self.closed:
            try:
                chunk = self.server.recv(1024).decode("ascii")
                if not chunk:
                    break
                    
                buffer += chunk
                
                try:
                    message = json.loads(buffer)
                    self.handle_response(message)
                    buffer = ""
                except json.JSONDecodeError:
                    if buffer.count("}") > 1:
                        #handle multiple messages that are stuck together
                        messages = buffer.replace("}{", "}|{").split("|")
                        for msg in messages:
                            try:
                                if msg:
                                    self.handle_response(json.loads(msg))
                            except:
                                pass
                        buffer = ""
            except Exception as e:
                print(f"Error in receive: {e}")
                break
        
        self.close()

    # if a player leaves this will run and notify the server on the connection loss
    def close(self):
        self.closed = True
        if hasattr(self, 'server') and self.server:
            try:
                self.server.close()
                print("Connection closed")
            except Exception as e:
                print(f"Error closing connection: {e}")

    # updates the client-side game based on the server messages
    def handle_response(self, response):
        r_type = response.get("type")
        data = response.get("data")

        if r_type == Protocols.Response.NICKNAME:
            print("Server requested nickname")
            
        elif r_type == Protocols.Response.BOARD_UPDATE:
            print(f"Board updated: {data}")
            self.play_board = data
            
        elif r_type == Protocols.Response.TURN:
            print("Your turn")
            self.current_turn = True
            
        elif r_type == Protocols.Response.OPPONENT_TURN:
            print("Opponent's turn")
            self.current_turn = False
            
        elif r_type == Protocols.Response.SYMBOL_ASSIGN:
            print(f"Assigned symbol: {data}")
            self.player_symbol = data
            
        elif r_type == Protocols.Response.OPPONENT:
            print(f"Opponent joined: {data}")
            self.opponent_name = data
            self.waiting_for_player = False
            
        elif r_type == Protocols.Response.START:
            print("Game started")
            self.started = True
            self.waiting_for_player = False
            
        elif r_type == Protocols.Response.WINNER:
            print(f"Winner: {data}")
            self.winner = data
            self.game_active = False
            
        elif r_type == Protocols.Response.DRAW:
            print("Game ended in draw")
            self.winner = "Draw"
            self.game_active = False
            
        elif r_type == Protocols.Response.OPPONENT_LEFT:
            print("Opponent left")
            self.opponent_name = None
            self.waiting_for_player = True
            self.started = False