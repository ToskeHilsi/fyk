"""
FlyKnight Game - Main Game Logic
Core game loop and state management
"""

import pygame
import math
import random
import time
from typing import Dict, Any, List, Optional
from config import *
from network import GameServer, GameClient, NetworkMessage
from dungeon import Dungeon, Room
from player import Player, Item
from enemy import EnemyManager, Enemy
from renderer import Renderer


class WorldItem:
    """Item dropped in the world"""
    
    def __init__(self, item_id: int, item: Item, x: float, y: float):
        self.item_id = item_id
        self.item = item
        self.x = x
        self.y = y
        self.pickup_radius = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'item_type': self.item.item_type,
            'item_class': self.item.item_class,
            'name': self.item.name,
            'x': self.x,
            'y': self.y
        }


class Game:
    """Main game class"""
    
    def __init__(self, is_host: bool = False, host_address: Optional[str] = None):
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Networking
        self.is_host = is_host
        self.server: Optional[GameServer] = None
        self.client: Optional[GameClient] = None
        self.player_id: Optional[int] = None
        
        # Game state
        self.dungeon: Optional[Dungeon] = None
        self.local_player: Optional[Player] = None
        self.players: Dict[int, Player] = {}
        self.enemy_manager = EnemyManager()
        self.world_items: Dict[int, WorldItem] = {}
        self.next_item_id = 0
        
        # UI state
        self.show_inventory = False
        self.game_state = "menu"  # menu, playing, game_over
        
        # Renderer
        self.renderer = Renderer(self.screen)
        
        # Setup networking
        if is_host:
            self._setup_host()
        elif host_address:
            self._connect_to_host(host_address)
    
    def _setup_host(self):
        """Setup as host"""
        self.server = GameServer()
        if self.server.start():
            # Connect to own server
            self.client = GameClient()
            if self.client.connect('localhost'):
                # Wait for player ID
                time.sleep(0.1)
                self.player_id = self.client.player_id
                
                # Setup callbacks
                self._setup_client_callbacks()
                
                # Generate dungeon
                self._generate_dungeon()
                
                print("Hosting game successfully")
                return True
        
        print("Failed to setup host")
        return False
    
    def _connect_to_host(self, host_address: str):
        """Connect to existing host"""
        self.client = GameClient()
        if self.client.connect(host_address):
            # Wait for player ID and game state
            time.sleep(0.2)
            self.player_id = self.client.player_id
            
            # Setup callbacks
            self._setup_client_callbacks()
            
            # Load game state from server
            self._sync_from_server()
            
            print("Connected to game successfully")
            return True
        
        print("Failed to connect to host")
        return False
    
    def _setup_client_callbacks(self):
        """Setup network message callbacks"""
        if not self.client:
            return
        
        self.client.register_callback('player_joined', self._on_player_joined)
        self.client.register_callback('player_left', self._on_player_left)
        self.client.register_callback('player_attack', self._on_player_attack)
        self.client.register_callback('enemy_died', self._on_enemy_died)
        self.client.register_callback('item_picked_up', self._on_item_picked_up)
    
    def _generate_dungeon(self):
        """Generate new dungeon (host only)"""
        if not self.is_host:
            return
        
        self.dungeon = Dungeon(level=1)
        self.dungeon.generate()
        
        # Spawn enemies
        self.enemy_manager.spawn_enemies(self.dungeon)
        
        # Create local player at spawn
        spawn_x, spawn_y = self.dungeon.get_spawn_position()
        self.local_player = Player(self.player_id, spawn_x, spawn_y)
        self.players[self.player_id] = self.local_player
        
        # Update server state
        if self.server:
            self.server.update_game_state({
                'dungeon': self.dungeon.to_dict(),
                'enemies': self.enemy_manager.to_dict(),
                'players': {self.player_id: self.local_player.to_dict()},
                'items': {}
            })
    
    def _sync_from_server(self):
        """Sync game state from server"""
        if not self.client:
            return
        
        game_state = self.client.get_game_state()
        
        # Load dungeon
        if 'dungeon' in game_state:
            dungeon_data = game_state['dungeon']
            self.dungeon = Dungeon(dungeon_data['level'])
            self.dungeon.rooms = [Room.from_dict(r) for r in dungeon_data['rooms']]
            # Note: corridors aren't synced but regenerated from room connections
        
        # Load players
        if 'players' in game_state:
            for player_id, player_data in game_state['players'].items():
                player = Player.from_dict(player_data)
                self.players[int(player_id)] = player
                
                if int(player_id) == self.player_id:
                    self.local_player = player
        
        # Load enemies
        if 'enemies' in game_state:
            self.enemy_manager.from_dict(game_state['enemies'])
        
        # Load items
        if 'items' in game_state:
            for item_id, item_data in game_state['items'].items():
                item = Item(item_data['item_type'], 
                          item_data['item_class'], 
                          item_data['name'])
                world_item = WorldItem(int(item_id), item, 
                                      item_data['x'], item_data['y'])
                self.world_items[int(item_id)] = world_item
        
        # If we don't have a local player yet, create one
        if not self.local_player and self.dungeon:
            spawn_x, spawn_y = self.dungeon.get_spawn_position()
            self.local_player = Player(self.player_id, spawn_x, spawn_y)
            self.players[self.player_id] = self.local_player
    
    def _on_player_joined(self, data: Dict[str, Any]):
        """Handle player joined"""
        player_id = data['player_id']
        if player_id not in self.players and self.dungeon:
            spawn_x, spawn_y = self.dungeon.get_spawn_position()
            player = Player(player_id, spawn_x, spawn_y, f"Player{player_id}")
            self.players[player_id] = player
    
    def _on_player_left(self, data: Dict[str, Any]):
        """Handle player left"""
        player_id = data['player_id']
        if player_id in self.players:
            del self.players[player_id]
    
    def _on_player_attack(self, data: Dict[str, Any]):
        """Handle another player's attack"""
        # Visual/audio feedback could go here
        pass
    
    def _on_enemy_died(self, data: Dict[str, Any]):
        """Handle enemy death"""
        enemy_id = data['enemy_id']
        drops = data.get('drops', [])
        
        # Spawn items
        if enemy_id in self.enemy_manager.enemies:
            enemy = self.enemy_manager.enemies[enemy_id]
            for drop_name in drops:
                self._spawn_item(drop_name, enemy.x, enemy.y)
        
        # Remove enemy (may already be removed)
        if enemy_id in self.enemy_manager.enemies:
            del self.enemy_manager.enemies[enemy_id]
    
    def _on_item_picked_up(self, data: Dict[str, Any]):
        """Handle item pickup"""
        item_id = data['item_id']
        if item_id in self.world_items:
            del self.world_items[item_id]
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self._handle_events()
            
            if self.game_state == "menu":
                self._update_menu()
                self._render_menu()
            elif self.game_state == "playing":
                self._update(dt)
                self._render()
            
            pygame.display.flip()
        
        self._cleanup()
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "playing":
                    if event.key == pygame.K_i:
                        self.show_inventory = not self.show_inventory
                    elif event.key == pygame.K_e:
                        self._try_pickup_item()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
    
    def _update_menu(self):
        """Update menu state"""
        # Simple menu - press SPACE to start
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.dungeon and self.local_player:
                self.game_state = "playing"
    
    def _update(self, dt: float):
        """Update game state"""
        if not self.local_player or not self.dungeon:
            return
        
        # Sync from network if client
        if self.client and not self.is_host:
            self._sync_from_server()
        
        # Input handling
        self._handle_input(dt)
        
        # Update local player
        self.local_player.update(dt)
        
        # Update enemies (host only)
        if self.is_host:
            attacks = self.enemy_manager.update(dt, list(self.players.values()), 
                                               self.dungeon)
            
            # Process enemy attacks
            for attack in attacks:
                target_id = attack['target_id']
                if target_id in self.players:
                    self.players[target_id].take_damage(attack['damage'])
        
        # Check room clearing
        if self.is_host:
            self._check_room_clearing()
        
        # Send player state to server
        if self.client:
            self.client.send_message(NetworkMessage('player_update', 
                                                   self.local_player.to_dict()))
        
        # Update server state (if host)
        if self.server:
            self.server.update_game_state({
                'players': {pid: p.to_dict() for pid, p in self.players.items()},
                'enemies': self.enemy_manager.to_dict(),
                'items': {iid: item.to_dict() for iid, item in self.world_items.items()}
            })
    
    def _handle_input(self, dt: float):
        """Handle player input"""
        if not self.local_player or self.show_inventory:
            return
        
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate facing angle
        world_mouse_x, world_mouse_y = self.renderer.camera.reverse(mouse_x, mouse_y)
        dx = world_mouse_x - self.local_player.x
        dy = world_mouse_y - self.local_player.y
        self.local_player.facing_angle = math.atan2(dy, dx)
        
        # Movement
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_s]:
            move_y += 1
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_d]:
            move_x += 1
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707
        
        # Sprint
        self.local_player.is_sprinting = keys[pygame.K_LSHIFT]
        
        # Apply movement
        if move_x != 0 or move_y != 0:
            self.local_player.move(move_x, move_y, dt)
        
        # Attack
        if mouse_buttons[0]:  # Left click
            if self.local_player.attack():
                self._process_attack()
        
        # Block
        if mouse_buttons[2]:  # Right click
            self.local_player.start_blocking()
        else:
            self.local_player.stop_blocking()
    
    def _process_attack(self):
        """Process player attack"""
        if not self.local_player or not self.is_host:
            # Only host processes attacks to avoid duplication
            return
        
        attack_data = self.local_player.get_attack_data()
        
        # Find enemies in range
        attack_range = attack_data['range']
        attack_angle = attack_data['angle']
        player_x = attack_data['x']
        player_y = attack_data['y']
        damage = attack_data['damage']
        
        # Check each enemy
        for enemy in list(self.enemy_manager.enemies.values()):
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= attack_range:
                # Check if in attack arc (90 degree cone)
                enemy_angle = math.atan2(dy, dx)
                angle_diff = abs(enemy_angle - attack_angle)
                
                # Normalize angle difference
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff
                
                if angle_diff <= math.pi / 4:  # 45 degrees on each side
                    # Hit!
                    drops = self.enemy_manager.damage_enemy(enemy.id, damage)
                    
                    if drops is not None:  # Enemy died
                        # Spawn items
                        for drop_name in drops:
                            self._spawn_item(drop_name, enemy.x, enemy.y)
                        
                        # Notify clients
                        if self.client:
                            self.client.send_message(NetworkMessage('enemy_damage', {
                                'enemy_id': enemy.id,
                                'damage': damage,
                                'drops': drops
                            }))
    
    def _spawn_item(self, item_name: str, x: float, y: float):
        """Spawn item in world"""
        # Parse item name to get type and class
        item_type = None
        item_class = item_name
        
        if any(w in item_name for w in ['sword', 'hammer', 'dagger', 'spear']):
            item_type = 'weapon'
        elif any(w in item_name for w in ['buckler', 'board', 'tower', 'shield']):
            item_type = 'shield'
        elif any(w in item_name for w in ['helmet', 'chestplate', 'greaves']):
            item_type = 'armor'
        
        if item_type:
            item = Item(item_type, item_class, item_name.replace('_', ' ').title())
            world_item = WorldItem(self.next_item_id, item, x, y)
            self.world_items[self.next_item_id] = world_item
            self.next_item_id += 1
    
    def _try_pickup_item(self):
        """Try to pick up nearby item"""
        if not self.local_player:
            return
        
        # Find nearest item
        nearest_item = None
        nearest_dist = float('inf')
        
        for item in self.world_items.values():
            dx = item.x - self.local_player.x
            dy = item.y - self.local_player.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= item.pickup_radius and dist < nearest_dist:
                nearest_item = item
                nearest_dist = dist
        
        # Pick it up
        if nearest_item:
            if self.local_player.add_to_inventory(nearest_item.item):
                # Remove from world
                item_id = nearest_item.item_id
                del self.world_items[item_id]
                
                # Notify server
                if self.client:
                    self.client.send_message(NetworkMessage('pickup_item', {
                        'item_id': item_id
                    }))
    
    def _check_room_clearing(self):
        """Check if any rooms have been cleared"""
        if not self.dungeon:
            return
        
        for room in self.dungeon.rooms:
            if not room.cleared:
                # Check if all enemies in room are dead
                room_has_enemies = any(
                    enemy.room_id == room.room_id 
                    for enemy in self.enemy_manager.enemies.values()
                )
                
                if not room_has_enemies:
                    room.cleared = True
    
    def _render(self):
        """Render game"""
        if self.show_inventory and self.local_player:
            self.renderer.draw_inventory(self.local_player)
        else:
            game_state = {
                'dungeon': self.dungeon,
                'players': self.players,
                'enemies': self.enemy_manager.enemies,
                'items': self.world_items
            }
            
            self.renderer.render_game(game_state, self.player_id)
    
    def _render_menu(self):
        """Render menu"""
        options = [
            "Press SPACE to start",
            "ESC to return to menu"
        ]
        self.renderer.draw_menu("FlyKnight", options, 0)
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.client:
            self.client.disconnect()
        
        if self.server:
            self.server.stop()
        
        pygame.quit()


def start_game(mode: str = "host", host_address: str = "localhost"):
    """Start the game"""
    if mode == "host":
        game = Game(is_host=True)
    else:
        game = Game(is_host=False, host_address=host_address)
    
    game.run()
