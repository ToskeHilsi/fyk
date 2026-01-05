# FlyKnight - Quick Reference Guide

## Installation & Running

```bash
# Install dependencies
pip install pygame

# Start the game
python main.py

# Or use the quick start script
python start.py
```

## Game Files Overview

| File | Purpose |
|------|---------|
| `main.py` | Game launcher with menu system |
| `game.py` | Core game logic and main game loop |
| `config.py` | All game configuration and constants |
| `network.py` | LAN multiplayer networking |
| `dungeon.py` | Procedural dungeon generation |
| `player.py` | Player character, inventory, equipment |
| `enemy.py` | Enemy AI and behaviors |
| `renderer.py` | Camera system and all rendering |
| `start.py` | Convenience launcher script |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |

## Controls at a Glance

| Key/Button | Action |
|------------|--------|
| WASD | Move |
| Shift | Sprint |
| Left Click | Attack |
| Right Click | Block |
| I | Inventory |
| E | Pick up item |
| ESC | Menu |

## Weapon Comparison

| Weapon | Damage | Speed | Range | Hands | Notes |
|--------|--------|-------|-------|-------|-------|
| Sword | 30 | 1.0x | 50 | 1 | Balanced starter weapon |
| Hammer | 60 | 0.5x | 50 | 2 | Slow but powerful |
| Daggers | 30 | 1.5x | 35 | 2 | Fast, short range |
| Spear | 30 | 0.6x | 75 | 2 | Long reach |

## Shield Comparison

| Shield | Block % | Stamina Cost | Notes |
|--------|---------|--------------|-------|
| Parrying Buckler | 30% | 5 | Light and efficient |
| Soldier Board | 50% | 10 | Balanced protection |
| Tower Shield | 70% | 15 | Maximum defense |

## Armor Set Comparison

| Set | Damage Reduction | Stamina Regen | Drop Source |
|-----|------------------|---------------|-------------|
| Knight | 30% | 100% | Starting gear |
| Samurai | 60% | 50% | Wasps (rare) |
| Ranger | 15% | 90% | Ants (rare) |

## Enemy Types

### Larva
- **HP**: 30
- **Behavior**: Wanders slowly, jumps at player when in sight
- **Spawn**: Groups of 5-8
- **Threat**: Low (swarm enemy)
- **Drops**: Swords (5%)

### Ant
- **HP**: 60
- **Behavior**: Chases player or shoots with bow (10% chance)
- **Spawn**: 1-2 per room
- **Threat**: Medium
- **Drops**: Swords, daggers, spears, shields, ranger armor

### Wasp
- **HP**: 100
- **Behavior**: Aggressive chaser, stays near spawn point
- **Spawn**: Solo
- **Threat**: High
- **Drops**: Hammers, tower shields, samurai armor (rare)

## Multiplayer Setup

### Host Game
1. Select "Host Game" from menu
2. Share your local IP with friends
3. They connect to your IP

### Join Game
1. Get host's IP address (e.g., 192.168.1.100)
2. Select "Join Game"
3. Enter host IP
4. Press Enter

### Find Your IP
- **Windows**: Open Command Prompt, type `ipconfig`
- **Mac/Linux**: Open Terminal, type `ifconfig` or `ip addr`

## Gameplay Tips

### Combat
- Attack in the direction you're facing (use mouse to aim)
- Blocking reduces damage but costs stamina
- You can't regenerate stamina while blocking
- Different weapons have different attack arcs

### Stamina Management
- Sprint only when necessary
- Don't hold block continuously
- Heavy armor reduces stamina regen
- Let stamina recharge between fights

### Equipment Strategy
- Two-handed weapons = no shield
- Complete armor sets give better bonuses
- Lighter armor = more mobility
- Heavier armor = more survivability

### Dungeon Exploration
- Clear rooms of enemies to unlock them
- Spawn room (first room) has no enemies
- Items drop randomly from enemies
- Pick up items quickly in multiplayer (first come, first serve)

## Configuration

Edit `config.py` to modify:
- Screen resolution (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
- Player stats (`PLAYER_MAX_HP`, `PLAYER_MAX_STAMINA`)
- Weapon/shield/armor stats
- Enemy stats and behaviors
- Drop rates
- Network port (default: 5555)

## Common Issues

**Can't connect to host**: 
- Verify IP address
- Check firewall settings
- Ensure same local network

**Inventory full**:
- Max 20 items
- Drop or equip items to make room

**Stamina draining fast**:
- Check your armor (Samurai set reduces regen)
- Stop sprinting/blocking
- Wait for natural regeneration

**No enemies spawning**:
- Enemies only spawn in non-spawn rooms
- Clear the spawn room first
- Each room has one enemy type

## Advanced Techniques

### Kiting
- Attack and retreat to avoid damage
- Works well with spear's long range
- Essential for wasps with light armor

### Stamina Bursting
- Sprint to engage
- Attack quickly
- Retreat to regenerate
- Repeat

### Shield Tanking
- Heavy armor + tower shield
- Block most damage
- Works best with teammates for support

### Speed Running
- Ranger armor for mobility
- Daggers for fast attacks
- Sprint between rooms
- Skip unnecessary fights

## Development Notes

The game uses:
- **Pygame** for rendering and input
- **Socket programming** for networking
- **Pickle** for object serialization
- **Threading** for concurrent server/client
- **Procedural generation** for dungeons

Key design decisions:
- Server-authoritative (host processes combat)
- Client-side prediction (smooth local movement)
- State synchronization at 30 Hz
- Entity-component-like architecture

## Performance Tips

- Close background applications
- Reduce screen resolution if laggy
- Limit to 2-3 players for best performance
- Host on computer with better specs

## Credits & License

FlyKnight - Educational example of multiplayer game development
Created as a demonstration of game programming concepts

Feel free to modify, extend, and learn from this codebase!
