"""
FlyKnight Game - Main Entry Point
Launch the game with options to host or join
"""

import pygame
import sys
from game import start_game
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, YELLOW, FPS


class Launcher:
    """Game launcher with menu to host or join"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FlyKnight - Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        self.running = True
        self.state = "main_menu"  # main_menu, join_input
        self.selected_option = 0
        self.host_input = ""
        
        self.main_menu_options = [
            "Host Game",
            "Join Game",
            "Quit"
        ]
    
    def run(self):
        """Main launcher loop"""
        while self.running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                
                self._handle_event(event)
            
            self._render()
            pygame.display.flip()
    
    def _handle_event(self, event):
        """Handle input events"""
        if self.state == "main_menu":
            self._handle_main_menu_event(event)
        elif self.state == "join_input":
            self._handle_join_input_event(event)
    
    def _handle_main_menu_event(self, event):
        """Handle main menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
            elif event.key == pygame.K_RETURN:
                self._execute_menu_option()
    
    def _handle_join_input_event(self, event):
        """Handle join game input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Start game as client
                if self.host_input.strip():
                    pygame.quit()
                    start_game(mode="join", host_address=self.host_input.strip())
                    self.running = False
            elif event.key == pygame.K_ESCAPE:
                self.state = "main_menu"
                self.host_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.host_input = self.host_input[:-1]
            else:
                # Add character to input
                if event.unicode.isprintable() and len(self.host_input) < 50:
                    self.host_input += event.unicode
    
    def _execute_menu_option(self):
        """Execute selected menu option"""
        option = self.main_menu_options[self.selected_option]
        
        if option == "Host Game":
            pygame.quit()
            start_game(mode="host")
            self.running = False
        elif option == "Join Game":
            self.state = "join_input"
            self.host_input = "localhost"
        elif option == "Quit":
            self.running = False
            pygame.quit()
            sys.exit()
    
    def _render(self):
        """Render launcher screen"""
        self.screen.fill(BLACK)
        
        if self.state == "main_menu":
            self._render_main_menu()
        elif self.state == "join_input":
            self._render_join_input()
    
    def _render_main_menu(self):
        """Render main menu"""
        # Title
        title = self.font.render("FlyKnight", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render("Insect Knight Dungeon Crawler", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Options
        start_y = 250
        for i, option in enumerate(self.main_menu_options):
            color = YELLOW if i == self.selected_option else WHITE
            text = self.small_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            self.screen.blit(text, text_rect)
            
            # Selection indicator
            if i == self.selected_option:
                indicator = self.small_font.render(">", True, YELLOW)
                self.screen.blit(indicator, (text_rect.left - 40, text_rect.top))
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "",
            "Game Controls:",
            "WASD - Move, SHIFT - Sprint",
            "Left Click - Attack",
            "Right Click - Block",
            "I - Inventory, E - Pickup",
        ]
        
        inst_y = SCREEN_HEIGHT - 250
        inst_font = pygame.font.Font(None, 20)
        for i, line in enumerate(instructions):
            inst_text = inst_font.render(line, True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y + i * 22))
            self.screen.blit(inst_text, inst_rect)
    
    def _render_join_input(self):
        """Render join game input screen"""
        # Title
        title = self.small_font.render("Join Game", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instruction
        instruction = self.small_font.render("Enter host IP address:", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(instruction, instruction_rect)
        
        # Input box
        box_width = 400
        box_height = 50
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 300
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), 2)
        
        # Input text
        input_text = self.small_font.render(self.host_input, True, WHITE)
        self.screen.blit(input_text, (box_x + 10, box_y + 12))
        
        # Instructions
        inst1 = pygame.font.Font(None, 24).render("Press ENTER to connect", True, WHITE)
        inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(inst1, inst1_rect)
        
        inst2 = pygame.font.Font(None, 24).render("Press ESC to go back", True, WHITE)
        inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH // 2, 430))
        self.screen.blit(inst2, inst2_rect)
        
        # Examples
        example_text = pygame.font.Font(None, 20).render(
            "Examples: localhost, 192.168.1.100, 10.0.0.5", 
            True, (150, 150, 150)
        )
        example_rect = example_text.get_rect(center=(SCREEN_WIDTH // 2, 480))
        self.screen.blit(example_text, example_rect)


def main():
    """Main entry point"""
    launcher = Launcher()
    launcher.run()


if __name__ == "__main__":
    main()
