"""
FlyKnight Game - Dungeon Generation
Procedural generation of dungeon rooms and layout
"""

import random
import math
from typing import List, Tuple, Dict, Any
from config import (ROOM_MIN_SIZE, ROOM_MAX_SIZE, ROOM_PADDING, 
                    ENEMY_STATS, TILE_SIZE)


class Room:
    """Represents a single dungeon room"""
    
    def __init__(self, x: int, y: int, width: int, height: int, room_id: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_id = room_id
        self.cleared = False
        self.connected_rooms: List[int] = []
        self.enemies: List[Dict[str, Any]] = []
        self.center = (x + width // 2, y + height // 2)
        
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside room"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_rect(self) -> Tuple[int, int, int, int]:
        """Get room as rectangle (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    def intersects(self, other: 'Room') -> bool:
        """Check if this room intersects another room"""
        return not (self.x + self.width + ROOM_PADDING < other.x or
                   other.x + other.width + ROOM_PADDING < self.x or
                   self.y + self.height + ROOM_PADDING < other.y or
                   other.y + other.height + ROOM_PADDING < self.y)
    
    def get_spawn_positions(self, count: int) -> List[Tuple[int, int]]:
        """Get random spawn positions within room"""
        positions = []
        margin = 50  # Keep enemies away from walls
        
        for _ in range(count):
            x = random.randint(self.x + margin, self.x + self.width - margin)
            y = random.randint(self.y + margin, self.y + self.height - margin)
            positions.append((x, y))
        
        return positions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert room to dictionary for network sync"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'room_id': self.room_id,
            'cleared': self.cleared,
            'connected_rooms': self.connected_rooms,
            'center': self.center
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Room':
        """Create room from dictionary"""
        room = Room(data['x'], data['y'], data['width'], 
                   data['height'], data['room_id'])
        room.cleared = data['cleared']
        room.connected_rooms = data['connected_rooms']
        return room


class Corridor:
    """Represents a corridor connecting two rooms"""
    
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], width: int = 60):
        self.start = start
        self.end = end
        self.width = width
        self.segments = self._create_segments()
    
    def _create_segments(self) -> List[Tuple[int, int, int, int]]:
        """Create rectangular segments for L-shaped corridor"""
        x1, y1 = self.start
        x2, y2 = self.end
        
        segments = []
        
        # Horizontal segment
        if x1 != x2:
            min_x = min(x1, x2)
            max_x = max(x1, x2)
            segments.append((min_x, y1 - self.width // 2, max_x - min_x, self.width))
        
        # Vertical segment
        if y1 != y2:
            min_y = min(y1, y2)
            max_y = max(y1, y2)
            segments.append((x2 - self.width // 2, min_y, self.width, max_y - min_y))
        
        return segments
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside corridor"""
        for seg_x, seg_y, seg_w, seg_h in self.segments:
            if (seg_x <= x <= seg_x + seg_w and 
                seg_y <= y <= seg_y + seg_h):
                return True
        return False


class Dungeon:
    """Represents a complete dungeon level"""
    
    def __init__(self, level: int = 1, base_rooms: int = 6):
        self.level = level
        self.room_count = base_rooms + (level - 1)
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.spawn_room: Optional[Room] = None
        
    def generate(self):
        """Generate the dungeon layout"""
        self._generate_rooms()
        self._connect_rooms()
        self._spawn_enemies()
        
    def _generate_rooms(self):
        """Generate random non-overlapping rooms"""
        max_attempts = 100
        room_id = 0
        
        # First room at origin (spawn room)
        width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        spawn_room = Room(0, 0, width, height, room_id)
        self.rooms.append(spawn_room)
        self.spawn_room = spawn_room
        room_id += 1
        
        # Generate remaining rooms
        while len(self.rooms) < self.room_count:
            attempts = 0
            placed = False
            
            while attempts < max_attempts and not placed:
                # Random size
                width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
                height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
                
                # Random position near existing rooms
                if self.rooms:
                    base_room = random.choice(self.rooms)
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE * 2)
                    x = int(base_room.center[0] + math.cos(angle) * distance - width // 2)
                    y = int(base_room.center[1] + math.sin(angle) * distance - height // 2)
                else:
                    x = random.randint(-1000, 1000)
                    y = random.randint(-1000, 1000)
                
                # Check for overlaps
                new_room = Room(x, y, width, height, room_id)
                
                overlaps = False
                for room in self.rooms:
                    if new_room.intersects(room):
                        overlaps = True
                        break
                
                if not overlaps:
                    self.rooms.append(new_room)
                    room_id += 1
                    placed = True
                
                attempts += 1
            
            # If couldn't place room, try with smaller size
            if not placed and len(self.rooms) < self.room_count:
                width = ROOM_MIN_SIZE
                height = ROOM_MIN_SIZE
                x = random.randint(-2000, 2000)
                y = random.randint(-2000, 2000)
                new_room = Room(x, y, width, height, room_id)
                
                overlaps = any(new_room.intersects(room) for room in self.rooms)
                if not overlaps:
                    self.rooms.append(new_room)
                    room_id += 1
    
    def _connect_rooms(self):
        """Connect rooms with corridors using minimum spanning tree"""
        if len(self.rooms) < 2:
            return
        
        connected = {0}  # Start with spawn room
        unconnected = set(range(1, len(self.rooms)))
        
        while unconnected:
            # Find closest unconnected room to any connected room
            min_dist = float('inf')
            best_pair = None
            
            for conn_idx in connected:
                for unconn_idx in unconnected:
                    conn_room = self.rooms[conn_idx]
                    unconn_room = self.rooms[unconn_idx]
                    
                    dist = math.sqrt(
                        (conn_room.center[0] - unconn_room.center[0]) ** 2 +
                        (conn_room.center[1] - unconn_room.center[1]) ** 2
                    )
                    
                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (conn_idx, unconn_idx)
            
            if best_pair:
                idx1, idx2 = best_pair
                room1 = self.rooms[idx1]
                room2 = self.rooms[idx2]
                
                # Create corridor
                corridor = Corridor(room1.center, room2.center)
                self.corridors.append(corridor)
                
                # Mark as connected
                room1.connected_rooms.append(idx2)
                room2.connected_rooms.append(idx1)
                connected.add(idx2)
                unconnected.remove(idx2)
        
        # Add some extra connections for interesting layout
        extra_connections = max(1, len(self.rooms) // 4)
        for _ in range(extra_connections):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            
            if room1 != room2 and room2.room_id not in room1.connected_rooms:
                corridor = Corridor(room1.center, room2.center)
                self.corridors.append(corridor)
                room1.connected_rooms.append(room2.room_id)
                room2.connected_rooms.append(room1.room_id)
    
    def _spawn_enemies(self):
        """Spawn enemies in each room (except spawn room)"""
        enemy_id = 0
        
        for room in self.rooms:
            if room == self.spawn_room:
                continue  # No enemies in spawn room
            
            # Choose random enemy type
            enemy_types = list(ENEMY_STATS.keys())
            weights = [ENEMY_STATS[et]['spawn_weight'] for et in enemy_types]
            enemy_type = random.choices(enemy_types, weights=weights)[0]
            
            # Get group size
            min_size, max_size = ENEMY_STATS[enemy_type]['group_size']
            group_size = random.randint(min_size, max_size)
            
            # Get spawn positions
            positions = room.get_spawn_positions(group_size)
            
            # Create enemies
            for pos in positions:
                enemy_data = {
                    'id': enemy_id,
                    'type': enemy_type,
                    'x': pos[0],
                    'y': pos[1],
                    'hp': ENEMY_STATS[enemy_type]['hp'],
                    'max_hp': ENEMY_STATS[enemy_type]['hp'],
                    'room_id': room.room_id,
                    'spawn_pos': pos,
                    'state': 'idle',  # idle, chasing, attacking
                    'target': None,
                    'last_attack': 0,
                    'velocity': [0, 0]
                }
                
                # Special attributes for ant archers
                if enemy_type == 'ant' and random.random() < ENEMY_STATS['ant']['bow_chance']:
                    enemy_data['has_bow'] = True
                    enemy_data['last_shot'] = 0
                else:
                    enemy_data['has_bow'] = False
                
                # Special attributes for larva
                if enemy_type == 'larva':
                    enemy_data['last_jump'] = 0
                
                room.enemies.append(enemy_data)
                enemy_id += 1
    
    def get_room_at(self, x: int, y: int) -> Optional[Room]:
        """Get room at given position"""
        for room in self.rooms:
            if room.contains_point(x, y):
                return room
        return None
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable (in room or corridor)"""
        # Check rooms
        for room in self.rooms:
            if room.contains_point(x, y):
                return True
        
        # Check corridors
        for corridor in self.corridors:
            if corridor.contains_point(x, y):
                return True
        
        return False
    
    def get_spawn_position(self) -> Tuple[int, int]:
        """Get spawn position (center of spawn room)"""
        if self.spawn_room:
            return self.spawn_room.center
        return (0, 0)
    
    def get_all_enemies(self) -> List[Dict[str, Any]]:
        """Get all enemies from all rooms"""
        enemies = []
        for room in self.rooms:
            enemies.extend(room.enemies)
        return enemies
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dungeon to dictionary for network sync"""
        return {
            'level': self.level,
            'room_count': self.room_count,
            'rooms': [room.to_dict() for room in self.rooms],
            'spawn_pos': self.get_spawn_position()
        }
