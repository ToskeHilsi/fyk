"""
FlyKnight Game - Player Entity
Player character with inventory, equipment, and combat
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from config import (PLAYER_SIZE, PLAYER_SPEED, PLAYER_SPRINT_MULTIPLIER,
                    PLAYER_MAX_HP, PLAYER_MAX_STAMINA, PLAYER_STAMINA_REGEN,
                    PLAYER_INVENTORY_SIZE, ATTACK_STAMINA_COST, 
                    BLOCK_STAMINA_COST_PER_HIT, SPRINT_STAMINA_COST,
                    WEAPON_STATS, SHIELD_STATS, ARMOR_STATS)


class Item:
    """Represents an inventory item"""
    
    def __init__(self, item_type: str, item_class: str, name: str):
        """
        item_type: weapon, shield, armor
        item_class: specific item (sword, helmet, etc)
        """
        self.item_type = item_type
        self.item_class = item_class
        self.name = name
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_type': self.item_type,
            'item_class': self.item_class,
            'name': self.name
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Item':
        return Item(data['item_type'], data['item_class'], data['name'])


class Player:
    """Player character"""
    
    def __init__(self, player_id: int, x: float = 0, y: float = 0, name: str = "FlyKnight"):
        self.player_id = player_id
        self.name = name
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        
        # Stats
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.stamina = PLAYER_MAX_STAMINA
        self.max_stamina = PLAYER_MAX_STAMINA
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.facing_angle = 0  # Radians, where mouse is pointing
        self.is_sprinting = False
        
        # Combat
        self.is_attacking = False
        self.is_blocking = False
        self.attack_time = 0
        self.attack_cooldown = 0
        self.last_damage_time = 0
        self.damage_immunity_duration = 0.5  # Half second immunity after hit
        
        # Inventory
        self.inventory: List[Optional[Item]] = [None] * PLAYER_INVENTORY_SIZE
        self.equipped: Dict[str, Optional[Item]] = {
            'weapon': None,
            'shield': None,
            'helmet': None,
            'chestplate': None,
            'greaves': None
        }
        
        # Start with knight armor and sword
        self._give_starting_equipment()
    
    def _give_starting_equipment(self):
        """Give player starting equipment"""
        # Knight armor
        self.equipped['helmet'] = Item('armor', 'knight_helmet', 'Knight Helmet')
        self.equipped['chestplate'] = Item('armor', 'knight_chestplate', 'Knight Chestplate')
        self.equipped['greaves'] = Item('armor', 'knight_greaves', 'Knight Greaves')
        
        # Sword
        self.equipped['weapon'] = Item('weapon', 'sword', 'Iron Sword')
    
    def update(self, dt: float):
        """Update player state"""
        # Update stamina
        stamina_regen = self._get_stamina_regen_rate()
        
        # Can't regen while blocking
        if not self.is_blocking:
            self.stamina = min(self.max_stamina, self.stamina + stamina_regen * dt)
        
        # Drain stamina while sprinting
        if self.is_sprinting and (self.velocity_x != 0 or self.velocity_y != 0):
            self.stamina -= SPRINT_STAMINA_COST * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.is_sprinting = False
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Update attack animation
        if self.is_attacking:
            self.attack_time += dt
            attack_duration = self._get_attack_duration()
            if self.attack_time >= attack_duration:
                self.is_attacking = False
                self.attack_time = 0
    
    def move(self, dx: float, dy: float, dt: float):
        """Move player with collision"""
        speed = PLAYER_SPEED
        
        # Sprint multiplier if sprinting and has stamina
        if self.is_sprinting and self.stamina > 0:
            speed *= PLAYER_SPRINT_MULTIPLIER
        
        self.velocity_x = dx * speed
        self.velocity_y = dy * speed
        
        # Apply movement
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
    
    def attack(self) -> bool:
        """Attempt to attack"""
        if self.attack_cooldown > 0 or self.is_attacking:
            return False
        
        # Check stamina
        weapon = self.equipped['weapon']
        if weapon:
            _, _, _, stamina_cost, _ = WEAPON_STATS.get(weapon.item_class, (0, 1, 0, 15, False))
        else:
            stamina_cost = 15
        
        if self.stamina < stamina_cost:
            return False
        
        # Start attack
        self.stamina -= stamina_cost
        self.is_attacking = True
        self.attack_time = 0
        self.attack_cooldown = self._get_attack_duration() + self._get_attack_cooldown()
        
        return True
    
    def start_blocking(self):
        """Start blocking with shield"""
        if self.equipped['shield'] and not self.is_attacking:
            self.is_blocking = True
    
    def stop_blocking(self):
        """Stop blocking"""
        self.is_blocking = False
    
    def take_damage(self, damage: float) -> bool:
        """Take damage, return True if hit"""
        current_time = time.time()
        
        # Check damage immunity
        if current_time - self.last_damage_time < self.damage_immunity_duration:
            return False
        
        # Apply blocking reduction
        if self.is_blocking and self.equipped['shield']:
            shield = self.equipped['shield']
            block_reduction, stamina_cost = SHIELD_STATS.get(
                shield.item_class, (0.3, 10)
            )
            
            # Check if has stamina to block
            if self.stamina >= stamina_cost:
                damage *= (1 - block_reduction)
                self.stamina -= stamina_cost
            # If not enough stamina, take full damage and stop blocking
            else:
                self.is_blocking = False
        
        # Apply armor reduction
        armor_reduction = self._get_armor_reduction()
        damage *= (1 - armor_reduction)
        
        # Apply damage
        self.hp -= damage
        self.last_damage_time = current_time
        
        if self.hp <= 0:
            self.hp = 0
            return True  # Player died
        
        return True
    
    def heal(self, amount: float):
        """Heal player"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def add_to_inventory(self, item: Item) -> bool:
        """Add item to inventory, return True if successful"""
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                return True
        return False
    
    def remove_from_inventory(self, slot: int) -> Optional[Item]:
        """Remove item from inventory slot"""
        if 0 <= slot < len(self.inventory):
            item = self.inventory[slot]
            self.inventory[slot] = None
            return item
        return None
    
    def equip_item(self, inventory_slot: int) -> bool:
        """Equip item from inventory"""
        if inventory_slot < 0 or inventory_slot >= len(self.inventory):
            return False
        
        item = self.inventory[inventory_slot]
        if item is None:
            return False
        
        # Determine equipment slot
        if item.item_type == 'weapon':
            slot = 'weapon'
            # If two-handed, unequip shield
            if item.item_class in WEAPON_STATS:
                _, _, _, _, two_handed = WEAPON_STATS[item.item_class]
                if two_handed and self.equipped['shield']:
                    # Put shield back in inventory
                    if not self.add_to_inventory(self.equipped['shield']):
                        return False  # No room for shield
                    self.equipped['shield'] = None
        
        elif item.item_type == 'shield':
            # Check if weapon is two-handed
            weapon = self.equipped['weapon']
            if weapon and weapon.item_class in WEAPON_STATS:
                _, _, _, _, two_handed = WEAPON_STATS[weapon.item_class]
                if two_handed:
                    return False  # Can't equip shield with two-handed weapon
            slot = 'shield'
        
        elif item.item_type == 'armor':
            # Determine armor slot from item class
            if 'helmet' in item.item_class:
                slot = 'helmet'
            elif 'chestplate' in item.item_class:
                slot = 'chestplate'
            elif 'greaves' in item.item_class:
                slot = 'greaves'
            else:
                return False
        else:
            return False
        
        # Swap with currently equipped item
        old_item = self.equipped[slot]
        self.equipped[slot] = item
        self.inventory[inventory_slot] = old_item
        
        return True
    
    def unequip_item(self, slot: str) -> bool:
        """Unequip item to inventory"""
        if slot not in self.equipped:
            return False
        
        item = self.equipped[slot]
        if item is None:
            return False
        
        # Find empty slot in inventory
        if self.add_to_inventory(item):
            self.equipped[slot] = None
            return True
        
        return False
    
    def _get_attack_duration(self) -> float:
        """Get attack animation duration"""
        weapon = self.equipped['weapon']
        if weapon and weapon.item_class in WEAPON_STATS:
            _, attack_speed, _, _, _ = WEAPON_STATS[weapon.item_class]
            return 0.3 / attack_speed  # Base duration modified by speed
        return 0.3
    
    def _get_attack_cooldown(self) -> float:
        """Get cooldown between attacks"""
        weapon = self.equipped['weapon']
        if weapon and weapon.item_class in WEAPON_STATS:
            _, attack_speed, _, _, _ = WEAPON_STATS[weapon.item_class]
            return 0.4 / attack_speed
        return 0.4
    
    def _get_attack_damage(self) -> float:
        """Get attack damage"""
        weapon = self.equipped['weapon']
        if weapon and weapon.item_class in WEAPON_STATS:
            damage, _, _, _, _ = WEAPON_STATS[weapon.item_class]
            return damage
        return 10  # Base unarmed damage
    
    def _get_attack_range(self) -> float:
        """Get attack range"""
        weapon = self.equipped['weapon']
        if weapon and weapon.item_class in WEAPON_STATS:
            _, _, attack_range, _, _ = WEAPON_STATS[weapon.item_class]
            return attack_range
        return 40  # Base unarmed range
    
    def _get_armor_reduction(self) -> float:
        """Get total damage reduction from armor"""
        # Check for full armor set
        helmet = self.equipped['helmet']
        chestplate = self.equipped['chestplate']
        greaves = self.equipped['greaves']
        
        if not (helmet and chestplate and greaves):
            return 0
        
        # Check if all pieces are from same set
        armor_set = None
        for set_name in ARMOR_STATS.keys():
            if (set_name in helmet.item_class and 
                set_name in chestplate.item_class and 
                set_name in greaves.item_class):
                armor_set = set_name
                break
        
        if armor_set:
            reduction, _ = ARMOR_STATS[armor_set]
            return reduction
        
        return 0
    
    def _get_stamina_regen_rate(self) -> float:
        """Get stamina regeneration rate"""
        base_regen = PLAYER_STAMINA_REGEN
        
        # Check armor penalty
        helmet = self.equipped['helmet']
        chestplate = self.equipped['chestplate']
        greaves = self.equipped['greaves']
        
        if helmet and chestplate and greaves:
            # Check for full set
            armor_set = None
            for set_name in ARMOR_STATS.keys():
                if (set_name in helmet.item_class and 
                    set_name in chestplate.item_class and 
                    set_name in greaves.item_class):
                    armor_set = set_name
                    break
            
            if armor_set:
                _, regen_multiplier = ARMOR_STATS[armor_set]
                base_regen *= regen_multiplier
        
        return base_regen
    
    def get_attack_data(self) -> Dict[str, Any]:
        """Get data about current attack"""
        return {
            'damage': self._get_attack_damage(),
            'range': self._get_attack_range(),
            'angle': self.facing_angle,
            'x': self.x,
            'y': self.y
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for network sync"""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'facing_angle': self.facing_angle,
            'is_attacking': self.is_attacking,
            'is_blocking': self.is_blocking,
            'is_sprinting': self.is_sprinting,
            'equipped': {k: v.to_dict() if v else None 
                        for k, v in self.equipped.items()}
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary"""
        player = Player(data['player_id'], data['x'], data['y'], data['name'])
        player.hp = data['hp']
        player.max_hp = data['max_hp']
        player.stamina = data['stamina']
        player.max_stamina = data['max_stamina']
        player.facing_angle = data['facing_angle']
        player.is_attacking = data['is_attacking']
        player.is_blocking = data['is_blocking']
        player.is_sprinting = data['is_sprinting']
        
        # Restore equipped items
        for slot, item_data in data['equipped'].items():
            if item_data:
                player.equipped[slot] = Item.from_dict(item_data)
            else:
                player.equipped[slot] = None
        
        return player
