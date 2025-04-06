import socket
import threading
import json
from protocols import Protocols
import time
from room import Room

# reference- https://github.com/techwithtim/Online-Python-Game
class Server:
    def __init__(self, host="127.0.0.1", port=55555): # initialize the server
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        self.closed = False
        
        self.client_names = {}
        self.opponent = {}
        self.rooms = {}
        self.wait_for_pair = None
        
        print(f"Server started on {host}:{port}")
        self.receive()
        
    # handle the connections, getting client nickname
    def handle_connect(self, client):
        while True:
            self.send(Protocols.Response.NICKNAME, None, client)
            try:
                message = json.loads(client.recv(1024).decode("ascii"))
                r_type = message.get("type")
                data = message.get("data")
                
                if r_type == Protocols.Request.NICKNAME:
                    self.client_names[client] = data
                    print(f"User {data} connected")
                else:
                    continue
                
                if not self.wait_for_pair:
                    self.wait_for_pair = client
                    print(f"Player {data} waiting for opponent")
                else:
                    self.create_room(client)
                break
            except Exception as e:
                print(f"Error handling connection: {e}")
                client.close()
                return
    
    
    # creating a room for two players with no additional connection interruptions
    def create_room(self, client):
        print("Creating room")
        room = Room(client, self.wait_for_pair)
        self.opponent[client] = self.wait_for_pair
        self.opponent[self.wait_for_pair] = client
        
        # Send client nicknames
        self.send(Protocols.Response.OPPONENT, self.client_names[client], self.wait_for_pair)
        self.send(Protocols.Response.OPPONENT, self.client_names[self.wait_for_pair], client)
        
        # assign markers
        self.send(Protocols.Response.SYMBOL_ASSIGN, 'O', client)
        self.send(Protocols.Response.SYMBOL_ASSIGN, 'X', self.wait_for_pair)
        
        # room reference
        self.rooms[client] = room
        self.rooms[self.wait_for_pair] = room
        
        # game starts
        self.send(Protocols.Response.BOARD_UPDATE, room.play_board, client)
        self.send(Protocols.Response.BOARD_UPDATE, room.play_board, self.wait_for_pair)
        self.send(Protocols.Response.TURN, None, self.wait_for_pair)  # X goes first
        self.send(Protocols.Response.START, None, client)
        self.send(Protocols.Response.START, None, self.wait_for_pair)
        
        print(f"Game started between {self.client_names[client]} and {self.client_names[self.wait_for_pair]}")
        self.wait_for_pair = None
    
    # handle
    def handle(self, client):
        self.handle_connect(client)
        
        while True:
            try:
                data = client.recv(1024).decode("ascii")
                if not data:
                    break
                message = json.loads(data)
                self.handle_receive(message, client)
            except Exception as e:
                print(f"Error handling client: {e}")
                break
            
        self.send_to_opponent(Protocols.Response.OPPONENT_LEFT, None, client)
        self.disconnect(client)
    
    # if a player leaves/ when both players leave, the disconnection process
    def disconnect(self, client):
        opponent = self.opponent.get(client)
        
        # handling player in waiting state
        if client == self.wait_for_pair:
            self.wait_for_pair = None
            
        if client in self.client_names:
            print(f"Player {self.client_names[client]} disconnected")
            del self.client_names[client]
            
        if opponent:
            if client in self.opponent:
                del self.opponent[client]
            if opponent in self.opponent:
                del self.opponent[opponent]
            
        if client in self.rooms:
            del self.rooms[client]
            
        if opponent and opponent in self.rooms:
            del self.rooms[opponent]
            
        client.close()
    
    # checking the moves and checking if players have rooms, uses program class to define a message type
    def handle_receive(self, message, client):
        r_type = message.get("type")
        data = message.get("data")
        
        if r_type == Protocols.Request.MOVE:
            room = self.rooms.get(client)
            opponent = self.opponent.get(client)
            
            if not room or not opponent:
                return
                
            result = room.make_move(client, data)
            
            if result == False:
                # invalid move
                return
                
            # updating board for both players
            self.send(Protocols.Response.BOARD_UPDATE, room.play_board, client)
            self.send(Protocols.Response.BOARD_UPDATE, room.play_board, opponent)
            
            if result == 'win':
                winner_name = self.client_names[client]
                self.send(Protocols.Response.WINNER, winner_name, client)
                self.send(Protocols.Response.WINNER, winner_name, opponent)
            elif result == 'draw':
                self.send(Protocols.Response.DRAW, None, client)
                self.send(Protocols.Response.DRAW, None, opponent)
            else:
                # turns switch
                self.send(Protocols.Response.OPPONENT_TURN, None, client)
                self.send(Protocols.Response.TURN, None, opponent)
        
    # directing message transmission for chats using ascii for the server
    def send(self, r_type, data, client):
        try:
            message = {"type": r_type, "data": data}
            message = json.dumps(message).encode("ascii")
            client.send(message)
        except Exception as e:
            print(f"Error sending to {self.client_names.get(client)}: {e}")

    # connect with client (new connections for new rooms)
    def receive(self):
        print("Waiting for connections...")
        while True:
            try:
                client, address = self.server.accept()  # Accept client connections
                print(f"Connected with {str(address)}")
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break

    # when a player makes a move the server would notify the other player
    def send_to_opponent(self, r_type, data, client):
        opponent = self.opponent.get(client)
        if not opponent:
            return
        self.send(r_type, data, opponent)

if __name__ == "__main__":
    server = Server()
