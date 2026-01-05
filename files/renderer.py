"""
FlyKnight Game - Rendering System
Camera and drawing functions for all game entities
"""

import pygame
import math
from typing import List, Dict, Any, Optional, Tuple
from config import *


class Camera:
    """Camera that follows the player"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
    
    def update(self, target_x: float, target_y: float):
        """Update camera position to follow target"""
        self.target_x = target_x
        self.target_y = target_y
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * CAMERA_SMOOTH
        self.y += (self.target_y - self.y) * CAMERA_SMOOTH
    
    def apply(self, x: float, y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        screen_x = x - self.x + self.width // 2
        screen_y = y - self.y + self.height // 2
        return (screen_x, screen_y)
    
    def reverse(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x - self.width // 2
        world_y = screen_y + self.y - self.height // 2
        return (world_x, world_y)


class Renderer:
    """Main rendering system"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.camera = Camera(screen.get_width(), screen.get_height())
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 36)
    
    def render_game(self, game_state: Dict[str, Any], local_player_id: int):
        """Render the entire game"""
        self.screen.fill(BLACK)
        
        # Get dungeon
        dungeon = game_state.get('dungeon')
        players = game_state.get('players', {})
        enemies = game_state.get('enemies', {})
        items = game_state.get('items', {})
        
        # Update camera to follow local player
        if local_player_id in players:
            player = players[local_player_id]
            self.camera.update(player.x, player.y)
        
        # Draw dungeon
        if dungeon:
            self._draw_dungeon(dungeon)
        
        # Draw items
        for item_id, item_data in items.items():
            self._draw_item(item_data)
        
        # Draw enemies
        for enemy_id, enemy in enemies.items():
            self._draw_enemy(enemy)
        
        # Draw players
        for player_id, player in players.items():
            self._draw_player(player, is_local=(player_id == local_player_id))
        
        # Draw UI
        if local_player_id in players:
            self._draw_ui(players[local_player_id])
    
    def _draw_dungeon(self, dungeon):
        """Draw dungeon rooms and corridors"""
        # Draw rooms
        for room in dungeon.rooms:
            screen_x, screen_y = self.camera.apply(room.x, room.y)
            
            # Room floor
            color = DARK_BROWN if room.cleared else BROWN
            pygame.draw.rect(self.screen, color, 
                           (screen_x, screen_y, room.width, room.height))
            
            # Room walls
            pygame.draw.rect(self.screen, DARK_GRAY, 
                           (screen_x, screen_y, room.width, room.height), 3)
            
            # Room number
            text = self.small_font.render(f"Room {room.room_id}", True, LIGHT_GRAY)
            self.screen.blit(text, (screen_x + 10, screen_y + 10))
        
        # Draw corridors
        for corridor in dungeon.corridors:
            for seg_x, seg_y, seg_w, seg_h in corridor.segments:
                screen_x, screen_y = self.camera.apply(seg_x, seg_y)
                pygame.draw.rect(self.screen, BROWN, 
                               (screen_x, screen_y, seg_w, seg_h))
                pygame.draw.rect(self.screen, DARK_GRAY, 
                               (screen_x, screen_y, seg_w, seg_h), 2)
    
    def _draw_player(self, player, is_local: bool = False):
        """Draw player character"""
        screen_x, screen_y = self.camera.apply(player.x, player.y)
        
        # Body (insect-like)
        body_color = BLUE if is_local else GREEN
        if player.hp <= 0:
            body_color = GRAY
        
        # Main body
        pygame.draw.circle(self.screen, body_color, 
                         (int(screen_x), int(screen_y)), player.size // 2)
        
        # Head
        head_x = screen_x + math.cos(player.facing_angle) * (player.size // 3)
        head_y = screen_y + math.sin(player.facing_angle) * (player.size // 3)
        pygame.draw.circle(self.screen, body_color, 
                         (int(head_x), int(head_y)), player.size // 3)
        
        # Eyes
        eye_offset = player.size // 6
        eye_angle_left = player.facing_angle + 0.3
        eye_angle_right = player.facing_angle - 0.3
        
        left_eye_x = head_x + math.cos(eye_angle_left) * eye_offset
        left_eye_y = head_y + math.sin(eye_angle_left) * eye_offset
        right_eye_x = head_x + math.cos(eye_angle_right) * eye_offset
        right_eye_y = head_y + math.sin(eye_angle_right) * eye_offset
        
        pygame.draw.circle(self.screen, BLACK, 
                         (int(left_eye_x), int(left_eye_y)), 3)
        pygame.draw.circle(self.screen, BLACK, 
                         (int(right_eye_x), int(right_eye_y)), 3)
        
        # Draw weapon
        if player.equipped.get('weapon'):
            self._draw_weapon(screen_x, screen_y, player.facing_angle, 
                            player.equipped['weapon'].item_class, 
                            player.is_attacking, player.attack_time)
        
        # Draw shield
        if player.is_blocking and player.equipped.get('shield'):
            self._draw_shield(screen_x, screen_y, player.facing_angle)
        
        # HP bar
        bar_width = 40
        bar_height = 5
        hp_ratio = player.hp / player.max_hp
        
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - player.size - 10
        
        pygame.draw.rect(self.screen, RED, 
                       (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, 
                       (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        
        # Name
        name_text = self.small_font.render(player.name, True, WHITE)
        name_rect = name_text.get_rect(center=(screen_x, bar_y - 10))
        self.screen.blit(name_text, name_rect)
    
    def _draw_weapon(self, x: float, y: float, angle: float, 
                     weapon_type: str, attacking: bool, attack_time: float):
        """Draw equipped weapon"""
        weapon_length = 30
        weapon_color = LIGHT_GRAY
        
        # Attack animation - swing the weapon
        if attacking:
            attack_progress = min(1.0, attack_time / 0.3)
            swing_angle = math.sin(attack_progress * math.pi) * 1.5
            angle += swing_angle
        
        # Adjust position based on weapon type
        if 'hammer' in weapon_type:
            weapon_length = 35
            weapon_color = GRAY
        elif 'dagger' in weapon_type:
            weapon_length = 20
        elif 'spear' in weapon_type:
            weapon_length = 45
        
        end_x = x + math.cos(angle) * weapon_length
        end_y = y + math.sin(angle) * weapon_length
        
        pygame.draw.line(self.screen, weapon_color, (x, y), (end_x, end_y), 4)
        
        # Weapon tip
        pygame.draw.circle(self.screen, weapon_color, (int(end_x), int(end_y)), 3)
    
    def _draw_shield(self, x: float, y: float, angle: float):
        """Draw equipped shield"""
        shield_angle = angle + math.pi / 2
        shield_dist = 20
        shield_x = x + math.cos(shield_angle) * shield_dist
        shield_y = y + math.sin(shield_angle) * shield_dist
        
        # Shield shape
        points = []
        shield_size = 15
        for i in range(5):
            point_angle = angle + (i / 5) * math.pi - math.pi / 2
            point_x = shield_x + math.cos(point_angle) * shield_size
            point_y = shield_y + math.sin(point_angle) * shield_size
            points.append((point_x, point_y))
        
        pygame.draw.polygon(self.screen, GRAY, points)
        pygame.draw.polygon(self.screen, WHITE, points, 2)
    
    def _draw_enemy(self, enemy):
        """Draw enemy"""
        screen_x, screen_y = self.camera.apply(enemy.x, enemy.y)
        
        # Different colors for different types
        if enemy.type == 'larva':
            color = YELLOW
        elif enemy.type == 'ant':
            color = RED if not enemy.has_bow else (150, 50, 100)
        elif enemy.type == 'wasp':
            color = (200, 150, 0)
        else:
            color = RED
        
        # Body
        size = enemy.size
        pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), size // 2)
        
        # Simple features
        if enemy.type == 'wasp':
            # Wings
            wing_offset = size // 2
            pygame.draw.line(self.screen, (200, 200, 200), 
                           (screen_x - wing_offset, screen_y - wing_offset),
                           (screen_x - wing_offset - 10, screen_y - wing_offset - 10), 2)
            pygame.draw.line(self.screen, (200, 200, 200), 
                           (screen_x + wing_offset, screen_y - wing_offset),
                           (screen_x + wing_offset + 10, screen_y - wing_offset - 10), 2)
        
        # HP bar
        bar_width = 30
        bar_height = 4
        hp_ratio = enemy.hp / enemy.max_hp
        
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - size - 8
        
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, 
                       (bar_x, bar_y, bar_width * hp_ratio, bar_height))
    
    def _draw_item(self, item_data: Dict[str, Any]):
        """Draw item on ground"""
        screen_x, screen_y = self.camera.apply(item_data['x'], item_data['y'])
        
        # Item glow
        pygame.draw.circle(self.screen, GOLD, (int(screen_x), int(screen_y)), 12)
        pygame.draw.circle(self.screen, YELLOW, (int(screen_x), int(screen_y)), 8)
        
        # Item icon (simple)
        item_type = item_data.get('item_type', 'unknown')
        text = self.small_font.render(item_type[0].upper(), True, BLACK)
        text_rect = text.get_rect(center=(screen_x, screen_y))
        self.screen.blit(text, text_rect)
    
    def _draw_ui(self, player):
        """Draw UI overlay"""
        padding = 10
        
        # HP bar
        hp_bar_width = 200
        hp_bar_height = 30
        hp_ratio = player.hp / player.max_hp
        
        hp_x = padding
        hp_y = padding
        
        pygame.draw.rect(self.screen, DARK_GRAY, 
                       (hp_x, hp_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.screen, RED, 
                       (hp_x, hp_y, hp_bar_width * hp_ratio, hp_bar_height))
        pygame.draw.rect(self.screen, WHITE, 
                       (hp_x, hp_y, hp_bar_width, hp_bar_height), 2)
        
        hp_text = self.font.render(f"HP: {int(player.hp)}/{int(player.max_hp)}", 
                                   True, WHITE)
        self.screen.blit(hp_text, (hp_x + 5, hp_y + 5))
        
        # Stamina bar
        stamina_bar_width = 200
        stamina_bar_height = 20
        stamina_ratio = player.stamina / player.max_stamina
        
        stamina_x = padding
        stamina_y = hp_y + hp_bar_height + 5
        
        pygame.draw.rect(self.screen, DARK_GRAY, 
                       (stamina_x, stamina_y, stamina_bar_width, stamina_bar_height))
        pygame.draw.rect(self.screen, YELLOW, 
                       (stamina_x, stamina_y, stamina_bar_width * stamina_ratio, stamina_bar_height))
        pygame.draw.rect(self.screen, WHITE, 
                       (stamina_x, stamina_y, stamina_bar_width, stamina_bar_height), 2)
        
        stamina_text = self.small_font.render(
            f"Stamina: {int(player.stamina)}/{int(player.max_stamina)}", 
            True, WHITE)
        self.screen.blit(stamina_text, (stamina_x + 5, stamina_y + 2))
        
        # Equipment display
        equip_x = padding
        equip_y = stamina_y + stamina_bar_height + 20
        
        equip_text = self.font.render("Equipment:", True, WHITE)
        self.screen.blit(equip_text, (equip_x, equip_y))
        
        y_offset = equip_y + 25
        for slot, item in player.equipped.items():
            if item:
                text = self.small_font.render(f"{slot.title()}: {item.name}", 
                                             True, LIGHT_GRAY)
                self.screen.blit(text, (equip_x + 10, y_offset))
                y_offset += 20
        
        # Controls help
        help_x = SCREEN_WIDTH - 250
        help_y = SCREEN_HEIGHT - 150
        
        help_texts = [
            "WASD - Move",
            "Shift - Sprint",
            "Left Click - Attack",
            "Right Click - Block",
            "I - Inventory",
            "E - Pickup Item"
        ]
        
        for i, text in enumerate(help_texts):
            help_text = self.small_font.render(text, True, LIGHT_GRAY)
            self.screen.blit(help_text, (help_x, help_y + i * 20))
    
    def draw_menu(self, title: str, options: List[str], selected: int):
        """Draw a menu"""
        self.screen.fill(BLACK)
        
        # Title
        title_text = self.large_font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Options
        start_y = 200
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50))
            self.screen.blit(option_text, option_rect)
    
    def draw_inventory(self, player):
        """Draw inventory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_width = 600
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(self.screen, DARK_GRAY, 
                       (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, 
                       (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title = self.large_font.render("Inventory", True, WHITE)
        self.screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # Equipped items
        equip_x = panel_x + 20
        equip_y = panel_y + 80
        
        equip_title = self.font.render("Equipped:", True, YELLOW)
        self.screen.blit(equip_title, (equip_x, equip_y))
        
        y_offset = equip_y + 30
        for slot, item in player.equipped.items():
            slot_text = f"{slot.title()}:"
            slot_render = self.small_font.render(slot_text, True, WHITE)
            self.screen.blit(slot_render, (equip_x, y_offset))
            
            if item:
                item_render = self.small_font.render(item.name, True, GREEN)
                self.screen.blit(item_render, (equip_x + 120, y_offset))
            else:
                empty_render = self.small_font.render("Empty", True, GRAY)
                self.screen.blit(empty_render, (equip_x + 120, y_offset))
            
            y_offset += 25
        
        # Inventory slots
        inv_x = panel_x + 300
        inv_y = panel_y + 80
        
        inv_title = self.font.render("Inventory:", True, YELLOW)
        self.screen.blit(inv_title, (inv_x, inv_y))
        
        slot_size = 40
        slots_per_row = 5
        
        for i in range(PLAYER_INVENTORY_SIZE):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = inv_x + col * (slot_size + 5)
            slot_y = inv_y + 40 + row * (slot_size + 5)
            
            # Slot background
            pygame.draw.rect(self.screen, DARK_GRAY, 
                           (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(self.screen, LIGHT_GRAY, 
                           (slot_x, slot_y, slot_size, slot_size), 2)
            
            # Item
            item = player.inventory[i]
            if item:
                item_text = self.small_font.render(item.name[0], True, GOLD)
                item_rect = item_text.get_rect(center=(slot_x + slot_size // 2, 
                                                       slot_y + slot_size // 2))
                self.screen.blit(item_text, item_rect)
        
        # Instructions
        inst_text = self.small_font.render("Press I to close", True, LIGHT_GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 30))
        self.screen.blit(inst_text, inst_rect)
