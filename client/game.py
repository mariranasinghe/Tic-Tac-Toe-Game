import pygame
from client import Client
from protocols import Protocols
import time

# reference- https://github.com/techwithtim/Online-Python-Game
# the constants used in the code
WIDTH = 600
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class TicTacToeGame:
    def __init__(self, client):
        pygame.init()
        self.client = client
        self.client.start()
        
        # state of the game
        self.state = "nickname"  # states such as nickname, waiting, playing, ended
        self.play_board = [' '] * 9
        self.game_active = True
        
        # input for nickname
        self.input_text = ""
        self.input_active = True
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 74)
        self.input_rect = pygame.Rect(WIDTH//2 - 140, HEIGHT//2, 280, 40)
    
    # handling the event 
    def handle_event(self, event):
        if self.state == "nickname":
            self.handle_nickname_input(event)
        elif self.state == "playing":
            self.handle_game_input(event)
    
    # inputing nickname and recording it while checking its length 
    def handle_nickname_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.input_text.strip():
                self.client.nickname = self.input_text
                self.client.send(Protocols.Request.NICKNAME, self.input_text)
                self.state = "waiting"
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                # nickname length limit
                if len(self.input_text) < 12:
                    self.input_text += event.unicode
    
    # detect mouse clicks 
    def handle_game_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.client.current_turn:
            x, y = pygame.mouse.get_pos()
            col = x // (WIDTH // 3)
            row = y // (HEIGHT // 3)
            position = row * 3 + col
            
            if 0 <= position < 9 and self.client.play_board[position] == ' ':
                self.client.send(Protocols.Request.MOVE, position)

    # rendering the game screen
    def draw_screen(self, screen):
        screen.fill(BLACK)
        
        if self.state == "nickname":
            self.draw_nickname_screen(screen)
        elif self.state == "waiting":
            self.draw_waiting_screen(screen)
        elif self.state == "playing":
            self.draw_game_screen(screen)
        elif self.state == "ended":
            self.draw_end_screen(screen)
    
    # rendering the nickname screen seen right as we run the program        
    def draw_nickname_screen(self, screen):
        # title
        title = self.title_font.render("Tic Tac Toe", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # instructions
        instruction = self.font.render("Enter your nickname:", True, WHITE)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 - 60))
        
        # input box
        pygame.draw.rect(screen, WHITE, self.input_rect, 2)
        text_surface = self.font.render(self.input_text, True, WHITE)
        screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
    
    # draw the waiting screen   
    def draw_waiting_screen(self, screen):
        
        # debug client state
        print(f"Client state: started={self.client.started}")
        
        # Check if we should transition to playing state
        if self.client.started:
            print("Transitioning to playing state!")
            self.state = "playing"
            return
            
        # Title
        title = self.title_font.render("Tic Tac Toe", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # Waiting message
        waiting_text = self.font.render("Waiting for another player...", True, WHITE)
        screen.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, HEIGHT//2))
        
        # Show a simple animation
        seconds = int(time.time()) % 4
        dots = "." * seconds
        wait_dots = self.font.render(dots, True, WHITE)
        screen.blit(wait_dots, (WIDTH//2, HEIGHT//2 + 40))
    
    #  draw the game screen including the grid lines
    def draw_game_screen(self, screen):
        # Draw the board
        cell_size = WIDTH // 3
        
        # Draw grid lines
        for i in range(1, 3):
            pygame.draw.line(screen, WHITE, (i*cell_size, 0), (i*cell_size, HEIGHT), 3)
            pygame.draw.line(screen, WHITE, (0, i*cell_size), (WIDTH, i*cell_size), 3)
        
        # Draw symbols
        for idx, symbol in enumerate(self.client.play_board):
            if symbol != ' ':
                x = (idx % 3) * cell_size + cell_size//2
                y = (idx // 3) * cell_size + cell_size//2
                color = BLUE if symbol == self.client.player_symbol else GREEN
                text = self.title_font.render(symbol, True, color)
                text_rect = text.get_rect(center=(x, y))
                screen.blit(text, text_rect)
        
        # Draw turn indicator
        turn_text = "Your turn" if self.client.current_turn else f"{self.client.opponent_name}'s turn"
        turn_surface = self.font.render(turn_text, True, WHITE)
        screen.blit(turn_surface, (10, 10))
        
        # draw player info
        player_text = f"You: {self.client.nickname} ({self.client.player_symbol})"
        opponent_text = f"Opponent: {self.client.opponent_name}"
        
        player_surface = self.font.render(player_text, True, WHITE)
        opponent_surface = self.font.render(opponent_text, True, WHITE)
        
        screen.blit(player_surface, (10, HEIGHT - 80))
        screen.blit(opponent_surface, (10, HEIGHT - 40))
        
        # Check for the end of the game
        if hasattr(self.client, "winner") and self.client.winner:
            self.state = "ended"
            
    def draw_end_screen(self, screen):
        screen.fill(BLACK)
        
        if self.client.winner == "Draw":
            result_text = "Draw!"
            color = BLUE
        elif self.client.winner == self.client.nickname:
            result_text = "You Won!"
            color = GREEN
        else:
            result_text = f"{self.client.winner} Wins!"
            color = RED
            
        result_surface = self.title_font.render(result_text, True, color)
        screen.blit(result_surface, (WIDTH//2 - result_surface.get_width()//2, HEIGHT//2 - 50))
        
        # Instruction to restart
        restart_text = "Close the window to play again"
        restart_surface = self.font.render(restart_text, True, WHITE)
        screen.blit(restart_surface, (WIDTH//2 - restart_surface.get_width()//2, HEIGHT//2 + 50))

    def run(self):
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tic Tac Toe")
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # update game state based on players data
            if self.client.waiting_for_player and self.state == "playing":
                self.state = "waiting"
                
            if self.client.started and self.state == "waiting":
                self.state = "playing"
                
            # process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)
            
            # Draw the correct screen
            self.draw_screen(screen)
            pygame.display.flip()
            clock.tick(30)
            
        self.client.close()
        pygame.quit()

if __name__ == "__main__":
    game = TicTacToeGame(Client())
    game.run()
