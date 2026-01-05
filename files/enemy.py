"""
FlyKnight Game - Enemy AI
AI behaviors for all enemy types
"""

import math
import random
import time
from typing import Dict, Any, List, Tuple, Optional
from config import ENEMY_STATS, DROP_RATES


class Enemy:
    """Base enemy class"""
    
    def __init__(self, enemy_data: Dict[str, Any]):
        self.id = enemy_data['id']
        self.type = enemy_data['type']
        self.x = enemy_data['x']
        self.y = enemy_data['y']
        self.spawn_pos = enemy_data.get('spawn_pos', (self.x, self.y))
        self.room_id = enemy_data['room_id']
        
        # Stats
        stats = ENEMY_STATS[self.type]
        self.size = stats['size']
        self.speed = stats['speed']
        self.hp = enemy_data['hp']
        self.max_hp = enemy_data['max_hp']
        self.damage = stats['damage']
        self.detection_range = stats['detection_range']
        
        # State
        self.state = enemy_data.get('state', 'idle')
        self.target = enemy_data.get('target')
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Combat
        self.last_attack = enemy_data.get('last_attack', 0)
        self.attack_cooldown = 1.0
        self.attack_range = 40
        
        # Type-specific
        self.has_bow = enemy_data.get('has_bow', False)
        if self.has_bow:
            self.last_shot = enemy_data.get('last_shot', 0)
        
        if self.type == 'larva':
            self.last_jump = enemy_data.get('last_jump', 0)
    
    def update(self, dt: float, players: List[Any], dungeon: Any) -> Optional[Dict[str, Any]]:
        """Update enemy AI, returns attack data if attacking"""
        if self.type == 'larva':
            return self._update_larva(dt, players)
        elif self.type == 'ant':
            return self._update_ant(dt, players)
        elif self.type == 'wasp':
            return self._update_wasp(dt, players, dungeon)
        return None
    
    def _update_larva(self, dt: float, players: List[Any]) -> Optional[Dict[str, Any]]:
        """Update larva behavior"""
        current_time = time.time()
        
        # Find closest player in line of sight
        closest_player = None
        min_dist = float('inf')
        
        for player in players:
            if player.hp <= 0:
                continue
            
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < self.detection_range and dist < min_dist:
                # Check line of sight (simple check)
                closest_player = player
                min_dist = dist
        
        if closest_player and current_time - self.last_jump > ENEMY_STATS['larva']['jump_cooldown']:
            # Jump toward player
            self.state = 'jumping'
            self.target = closest_player.player_id
            
            dx = closest_player.x - self.x
            dy = closest_player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 0:
                jump_speed = ENEMY_STATS['larva']['jump_speed']
                self.velocity_x = (dx / dist) * jump_speed
                self.velocity_y = (dy / dist) * jump_speed
                self.last_jump = current_time
        else:
            # Random slow movement
            if random.random() < 0.02:  # 2% chance to change direction each frame
                angle = random.uniform(0, 2 * math.pi)
                self.velocity_x = math.cos(angle) * self.speed * 0.5
                self.velocity_y = math.sin(angle) * self.speed * 0.5
            
            self.state = 'wandering'
        
        # Apply velocity with decay
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_x *= 0.9
        self.velocity_y *= 0.9
        
        # Check for collision with player
        if closest_player and min_dist < self.attack_range:
            if current_time - self.last_attack > self.attack_cooldown:
                self.last_attack = current_time
                return {
                    'enemy_id': self.id,
                    'target_id': closest_player.player_id,
                    'damage': self.damage
                }
        
        return None
    
    def _update_ant(self, dt: float, players: List[Any]) -> Optional[Dict[str, Any]]:
        """Update ant behavior"""
        current_time = time.time()
        
        # Find closest player
        closest_player = None
        min_dist = float('inf')
        
        for player in players:
            if player.hp <= 0:
                continue
            
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < self.detection_range and dist < min_dist:
                closest_player = player
                min_dist = dist
        
        if self.has_bow:
            # Archer behavior - stay at range and shoot
            if closest_player:
                self.state = 'attacking'
                self.target = closest_player.player_id
                
                # Keep distance
                if min_dist < ENEMY_STATS['ant']['bow_range'] * 0.7:
                    # Too close, back away
                    dx = self.x - closest_player.x
                    dy = self.y - closest_player.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0:
                        self.velocity_x = (dx / dist) * self.speed
                        self.velocity_y = (dy / dist) * self.speed
                else:
                    self.velocity_x = 0
                    self.velocity_y = 0
                
                # Shoot
                if min_dist < ENEMY_STATS['ant']['bow_range']:
                    if current_time - self.last_shot > ENEMY_STATS['ant']['bow_cooldown']:
                        self.last_shot = current_time
                        return {
                            'enemy_id': self.id,
                            'target_id': closest_player.player_id,
                            'damage': self.damage * 0.8,  # Ranged does less damage
                            'ranged': True
                        }
            else:
                self.state = 'idle'
                self.velocity_x = 0
                self.velocity_y = 0
        else:
            # Melee behavior
            if closest_player:
                self.state = 'chasing'
                self.target = closest_player.player_id
                
                # Chase player
                if min_dist > self.attack_range:
                    dx = closest_player.x - self.x
                    dy = closest_player.y - self.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0:
                        self.velocity_x = (dx / dist) * self.speed
                        self.velocity_y = (dy / dist) * self.speed
                else:
                    # In attack range
                    self.velocity_x = 0
                    self.velocity_y = 0
                    
                    if current_time - self.last_attack > self.attack_cooldown:
                        self.last_attack = current_time
                        return {
                            'enemy_id': self.id,
                            'target_id': closest_player.player_id,
                            'damage': self.damage
                        }
            else:
                # Wander
                self.state = 'wandering'
                if random.random() < 0.01:
                    angle = random.uniform(0, 2 * math.pi)
                    self.velocity_x = math.cos(angle) * self.speed * 0.3
                    self.velocity_y = math.sin(angle) * self.speed * 0.3
        
        # Apply movement
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        return None
    
    def _update_wasp(self, dt: float, players: List[Any], dungeon: Any) -> Optional[Dict[str, Any]]:
        """Update wasp behavior"""
        current_time = time.time()
        
        # Find closest player
        closest_player = None
        min_dist = float('inf')
        
        for player in players:
            if player.hp <= 0:
                continue
            
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < self.detection_range and dist < min_dist:
                closest_player = player
                min_dist = dist
        
        if closest_player:
            self.state = 'chasing'
            self.target = closest_player.player_id
            
            # Chase player aggressively
            if min_dist > self.attack_range:
                dx = closest_player.x - self.x
                dy = closest_player.y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    self.velocity_x = (dx / dist) * self.speed
                    self.velocity_y = (dy / dist) * self.speed
            else:
                # In attack range
                self.velocity_x *= 0.5
                self.velocity_y *= 0.5
                
                if current_time - self.last_attack > self.attack_cooldown:
                    self.last_attack = current_time
                    return {
                        'enemy_id': self.id,
                        'target_id': closest_player.player_id,
                        'damage': self.damage
                    }
        else:
            # Wander near spawn
            self.state = 'wandering'
            
            # Stay near spawn position
            dx = self.spawn_pos[0] - self.x
            dy = self.spawn_pos[1] - self.y
            dist_from_spawn = math.sqrt(dx * dx + dy * dy)
            
            if dist_from_spawn > ENEMY_STATS['wasp']['wander_radius']:
                # Return to spawn area
                if dist_from_spawn > 0:
                    self.velocity_x = (dx / dist_from_spawn) * self.speed * 0.5
                    self.velocity_y = (dy / dist_from_spawn) * self.speed * 0.5
            else:
                # Random movement
                if random.random() < 0.02:
                    angle = random.uniform(0, 2 * math.pi)
                    self.velocity_x = math.cos(angle) * self.speed * 0.4
                    self.velocity_y = math.sin(angle) * self.speed * 0.4
        
        # Apply movement
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        return None
    
    def take_damage(self, damage: float) -> bool:
        """Take damage, return True if died"""
        self.hp -= damage
        return self.hp <= 0
    
    def get_drops(self) -> List[str]:
        """Generate item drops"""
        drops = []
        
        if self.type in DROP_RATES:
            for item_name, drop_chance in DROP_RATES[self.type].items():
                if random.random() < drop_chance:
                    drops.append(item_name)
        
        return drops
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert enemy to dictionary"""
        data = {
            'id': self.id,
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'state': self.state,
            'target': self.target,
            'room_id': self.room_id,
            'spawn_pos': self.spawn_pos,
            'last_attack': self.last_attack,
            'velocity': [self.velocity_x, self.velocity_y]
        }
        
        if self.has_bow:
            data['has_bow'] = True
            data['last_shot'] = self.last_shot
        
        if self.type == 'larva':
            data['last_jump'] = self.last_jump
        
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Enemy':
        """Create enemy from dictionary"""
        return Enemy(data)


class EnemyManager:
    """Manages all enemies in the game"""
    
    def __init__(self):
        self.enemies: Dict[int, Enemy] = {}
        self.next_enemy_id = 0
    
    def spawn_enemies(self, dungeon):
        """Spawn enemies from dungeon data"""
        self.enemies.clear()
        
        all_enemies = dungeon.get_all_enemies()
        for enemy_data in all_enemies:
            enemy = Enemy(enemy_data)
            self.enemies[enemy.id] = enemy
            self.next_enemy_id = max(self.next_enemy_id, enemy.id + 1)
    
    def update(self, dt: float, players: List[Any], dungeon: Any) -> List[Dict[str, Any]]:
        """Update all enemies, returns list of attacks"""
        attacks = []
        
        for enemy in list(self.enemies.values()):
            attack = enemy.update(dt, players, dungeon)
            if attack:
                attacks.append(attack)
        
        return attacks
    
    def damage_enemy(self, enemy_id: int, damage: float) -> Optional[List[str]]:
        """Damage enemy, returns drops if died"""
        if enemy_id not in self.enemies:
            return None
        
        enemy = self.enemies[enemy_id]
        died = enemy.take_damage(damage)
        
        if died:
            drops = enemy.get_drops()
            del self.enemies[enemy_id]
            return drops
        
        return None
    
    def get_enemies_in_range(self, x: float, y: float, range: float) -> List[Enemy]:
        """Get enemies within range of position"""
        in_range = []
        
        for enemy in self.enemies.values():
            dx = enemy.x - x
            dy = enemy.y - y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist <= range:
                in_range.append(enemy)
        
        return in_range
    
    def to_dict(self) -> Dict[int, Dict[str, Any]]:
        """Convert all enemies to dictionary"""
        return {enemy_id: enemy.to_dict() 
                for enemy_id, enemy in self.enemies.items()}
    
    def from_dict(self, data: Dict[int, Dict[str, Any]]):
        """Load enemies from dictionary"""
        self.enemies.clear()
        for enemy_id, enemy_data in data.items():
            self.enemies[int(enemy_id)] = Enemy.from_dict(enemy_data)
