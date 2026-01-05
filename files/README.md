# FlyKnight - 2D Dungeon Crawler

A multiplayer insect-themed dungeon crawler with procedurally generated dungeons and LAN networking support.

## Features

### Gameplay
- **Procedurally Generated Dungeons**: Each playthrough features unique room layouts
- **Three Enemy Types**: 
  - Larva: Small, jumpy enemies that spawn in groups
  - Ants: Medium enemies with melee and ranged variants
  - Wasps: Large, tough enemies that guard their territory
- **Equipment System**: Collect and equip weapons, shields, and armor
- **Combat**: Real-time combat with stamina management
- **Multiplayer**: Support for 1-4 players over LAN

### Weapons
- **Sword**: Balanced one-handed weapon
- **Hammer**: Slow but devastating two-handed weapon
- **Daggers**: Fast two-handed dual weapons with short range
- **Spear**: Long-range two-handed weapon

### Shields
- **Parrying Buckler**: Light shield with low stamina cost
- **Soldier Board**: Balanced medium shield
- **Tower Shield**: Heavy shield with maximum protection

### Armor Sets
- **Knight Set**: Starting balanced armor
- **Samurai Set**: High protection, heavy stamina penalty
- **Ranger Set**: Light armor with minimal penalties

## Installation

### Requirements
- Python 3.8 or higher
- Pygame 2.0 or higher

### Setup
```bash
# Install dependencies
pip install pygame

# Run the game
python main.py
```

## How to Play

### Starting a Game
1. **Host Game**: Start a new game server that others can join
2. **Join Game**: Connect to an existing game using the host's IP address
   - For local testing, use `localhost`
   - For LAN play, use the host's local IP (e.g., `192.168.1.100`)

### Controls
- **WASD**: Move your FlyKnight
- **Shift**: Sprint (consumes stamina)
- **Left Click**: Attack with equipped weapon
- **Right Click (Hold)**: Block with shield (if equipped)
- **I**: Open/close inventory
- **E**: Pick up nearby items
- **ESC**: Return to menu

### Gameplay Tips
1. **Stamina Management**: 
   - Attacking, blocking, and sprinting all consume stamina
   - Stamina doesn't regenerate while blocking
   - Certain armor reduces stamina regeneration

2. **Equipment Strategy**:
   - Two-handed weapons prevent shield use
   - Complete armor sets provide better protection
   - Match your playstyle: heavy armor for tanking, light for mobility

3. **Combat**:
   - Attack enemies within your weapon's arc
   - Block incoming attacks to reduce damage
   - Use terrain and kiting for tough enemies

4. **Multiplayer**:
   - Work together to clear rooms faster
   - Items are first-come, first-served
   - All players share the same dungeon instance

## Network Setup for LAN Play

### Finding Your IP Address

**Windows**:
```cmd
ipconfig
```
Look for "IPv4 Address" under your network adapter (e.g., `192.168.1.100`)

**Mac/Linux**:
```bash
ifconfig
# or
ip addr show
```
Look for `inet` address under your network interface (e.g., `192.168.1.100`)

### Hosting
1. Start the game and select "Host Game"
2. Share your local IP address with other players
3. Make sure all players are on the same local network

### Joining
1. Get the host's IP address
2. Select "Join Game"
3. Enter the host's IP address
4. Press Enter to connect

### Firewall Notes
- The game uses port 5555 by default
- You may need to allow the game through your firewall
- For Windows Firewall: Allow Python through when prompted

## Architecture

The game is built with a modular architecture:

- **network.py**: LAN multiplayer with server-client architecture
- **dungeon.py**: Procedural dungeon generation
- **player.py**: Player character with inventory and equipment
- **enemy.py**: AI behaviors for all enemy types
- **renderer.py**: Camera system and rendering
- **game.py**: Core game logic and state management
- **config.py**: Game configuration and constants

### Network Architecture
- **Server (Host)**: Runs on the hosting player's machine
  - Manages authoritative game state
  - Processes combat and enemy AI
  - Broadcasts updates to all clients
  
- **Client**: Every player (including host) runs a client
  - Sends local player input to server
  - Receives game state updates
  - Renders game locally

## Development

### Adding New Weapons
Edit `config.py` and add to `WEAPON_STATS`:
```python
'new_weapon': (damage, attack_speed, range, stamina_cost, two_handed)
```

### Adding New Enemies
1. Add stats to `ENEMY_STATS` in `config.py`
2. Add behavior in `enemy.py` Enemy class
3. Add drop rates in `DROP_RATES`

### Modifying Dungeon Generation
Edit `dungeon.py`:
- `_generate_rooms()`: Room placement logic
- `_connect_rooms()`: Corridor generation
- `_spawn_enemies()`: Enemy spawning rules

## Known Limitations

- Items are synchronized but not prevented from duplicate pickup (race conditions possible)
- No player collision (players can overlap)
- Enemy pathfinding is simple line-of-sight
- No save/load functionality
- Limited to local network play (no internet matchmaking)

## Future Enhancements

Possible additions:
- More enemy types and boss battles
- Procedural item generation with random stats
- Persistent progression between runs
- More armor and weapon varieties
- Spells and ranged weapons for players
- Dungeon themes with different tilesets
- Boss rooms and special encounters
- Trading system between players

## Troubleshooting

**"Connection refused" when joining**:
- Verify the host's IP address
- Ensure host has started the game
- Check firewall settings
- Confirm both players are on same network

**Game is laggy**:
- Check network connection quality
- Reduce number of simultaneous players
- Close background applications

**Can't pick up items**:
- Make sure inventory isn't full (20 item limit)
- Get closer to the item (press E when near)
- Another player may have grabbed it first

**Enemies aren't spawning**:
- Enemies only spawn in non-spawn rooms
- Check if dungeon generated correctly
- Try restarting as host

## Credits

Created as a comprehensive example of a 2D multiplayer dungeon crawler using Python and Pygame.

Demonstrates:
- Network programming with sockets
- Procedural generation
- Game AI and pathfinding
- Entity-component-like architecture
- Real-time multiplayer game state synchronization
