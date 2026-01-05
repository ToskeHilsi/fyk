"""
FlyKnight Game - Networking Module
Handles LAN multiplayer with socket-based communication
"""

import socket
import pickle
import threading
import time
from typing import Dict, Any, Optional, List
from config import DEFAULT_PORT, MAX_PLAYERS, NETWORK_TICK_RATE


class NetworkMessage:
    """Base class for network messages"""
    def __init__(self, msg_type: str, data: Any):
        self.type = msg_type
        self.data = data
        self.timestamp = time.time()


class GameServer:
    """Server that hosts the game session"""
    
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[int, socket.socket] = {}  # player_id -> socket
        self.client_addresses: Dict[int, tuple] = {}
        self.next_player_id = 0
        self.running = False
        self.game_state: Dict[str, Any] = {
            'players': {},
            'enemies': {},
            'items': {},
            'rooms': [],
            'dungeon_level': 1
        }
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server"""
        try:
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(MAX_PLAYERS)
            self.running = True
            
            # Start server threads
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            update_thread = threading.Thread(target=self._update_loop, daemon=True)
            accept_thread.start()
            update_thread.start()
            
            print(f"Server started on port {self.port}")
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the server"""
        self.running = False
        for client in self.clients.values():
            try:
                client.close()
            except:
                pass
        self.socket.close()
        print("Server stopped")
    
    def _accept_connections(self):
        """Accept new client connections"""
        self.socket.settimeout(1.0)
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                if len(self.clients) >= MAX_PLAYERS:
                    client_socket.close()
                    continue
                
                player_id = self.next_player_id
                self.next_player_id += 1
                
                with self.lock:
                    self.clients[player_id] = client_socket
                    self.client_addresses[player_id] = address
                
                # Send welcome message with player ID
                self._send_to_client(client_socket, NetworkMessage('welcome', {
                    'player_id': player_id,
                    'game_state': self.game_state
                }))
                
                # Notify other clients
                self._broadcast(NetworkMessage('player_joined', {'player_id': player_id}), 
                              exclude=player_id)
                
                # Start handling this client
                thread = threading.Thread(target=self._handle_client, 
                                        args=(player_id, client_socket), 
                                        daemon=True)
                thread.start()
                
                print(f"Player {player_id} connected from {address}")
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _handle_client(self, player_id: int, client_socket: socket.socket):
        """Handle messages from a specific client"""
        client_socket.settimeout(5.0)
        
        while self.running:
            try:
                data = self._receive_from_client(client_socket)
                if data is None:
                    break
                
                # Process message
                self._process_message(player_id, data)
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error handling client {player_id}: {e}")
                break
        
        # Client disconnected
        self._remove_client(player_id)
    
    def _process_message(self, player_id: int, message: NetworkMessage):
        """Process incoming message from client"""
        with self.lock:
            if message.type == 'player_update':
                # Update player state
                if 'players' not in self.game_state:
                    self.game_state['players'] = {}
                self.game_state['players'][player_id] = message.data
                
            elif message.type == 'attack':
                # Broadcast attack to all clients
                self._broadcast(NetworkMessage('player_attack', {
                    'player_id': player_id,
                    'attack_data': message.data
                }))
                
            elif message.type == 'enemy_damage':
                # Update enemy health
                enemy_id = message.data['enemy_id']
                damage = message.data['damage']
                if enemy_id in self.game_state.get('enemies', {}):
                    enemy = self.game_state['enemies'][enemy_id]
                    enemy['hp'] -= damage
                    if enemy['hp'] <= 0:
                        # Enemy died
                        del self.game_state['enemies'][enemy_id]
                        self._broadcast(NetworkMessage('enemy_died', {
                            'enemy_id': enemy_id,
                            'drops': message.data.get('drops', [])
                        }))
                    else:
                        self._broadcast(NetworkMessage('enemy_damaged', {
                            'enemy_id': enemy_id,
                            'hp': enemy['hp']
                        }))
                        
            elif message.type == 'pickup_item':
                # Remove item from world
                item_id = message.data['item_id']
                if item_id in self.game_state.get('items', {}):
                    del self.game_state['items'][item_id]
                    self._broadcast(NetworkMessage('item_picked_up', {
                        'item_id': item_id,
                        'player_id': player_id
                    }))
    
    def _update_loop(self):
        """Main server update loop - broadcasts game state"""
        tick_time = 1.0 / NETWORK_TICK_RATE
        
        while self.running:
            start_time = time.time()
            
            with self.lock:
                # Broadcast game state to all clients
                state_message = NetworkMessage('game_state', self.game_state)
                self._broadcast(state_message)
            
            # Sleep to maintain tick rate
            elapsed = time.time() - start_time
            sleep_time = max(0, tick_time - elapsed)
            time.sleep(sleep_time)
    
    def _broadcast(self, message: NetworkMessage, exclude: Optional[int] = None):
        """Send message to all clients except excluded"""
        dead_clients = []
        for player_id, client_socket in self.clients.items():
            if exclude is not None and player_id == exclude:
                continue
            try:
                self._send_to_client(client_socket, message)
            except:
                dead_clients.append(player_id)
        
        # Clean up dead connections
        for player_id in dead_clients:
            self._remove_client(player_id)
    
    def _send_to_client(self, client_socket: socket.socket, message: NetworkMessage):
        """Send message to specific client"""
        data = pickle.dumps(message)
        size = len(data)
        client_socket.sendall(size.to_bytes(4, 'big') + data)
    
    def _receive_from_client(self, client_socket: socket.socket) -> Optional[NetworkMessage]:
        """Receive message from client"""
        # Read size header
        size_data = client_socket.recv(4)
        if not size_data or len(size_data) < 4:
            return None
        
        size = int.from_bytes(size_data, 'big')
        
        # Read message data
        data = b''
        while len(data) < size:
            chunk = client_socket.recv(min(size - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        return pickle.loads(data)
    
    def _remove_client(self, player_id: int):
        """Remove disconnected client"""
        with self.lock:
            if player_id in self.clients:
                try:
                    self.clients[player_id].close()
                except:
                    pass
                del self.clients[player_id]
                
                if player_id in self.client_addresses:
                    del self.client_addresses[player_id]
                
                # Remove from game state
                if player_id in self.game_state.get('players', {}):
                    del self.game_state['players'][player_id]
                
                # Notify other clients
                self._broadcast(NetworkMessage('player_left', {'player_id': player_id}))
                
                print(f"Player {player_id} disconnected")
    
    def update_game_state(self, state_update: Dict[str, Any]):
        """Update server's game state (called by game logic)"""
        with self.lock:
            self.game_state.update(state_update)


class GameClient:
    """Client that connects to game server"""
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.player_id: Optional[int] = None
        self.game_state: Dict[str, Any] = {}
        self.lock = threading.Lock()
        self.message_callbacks: Dict[str, List] = {}
        
    def connect(self, host: str, port: int = DEFAULT_PORT) -> bool:
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((host, port))
            self.connected = True
            
            # Start receive thread
            thread = threading.Thread(target=self._receive_loop, daemon=True)
            thread.start()
            
            print(f"Connected to server at {host}:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Disconnected from server")
    
    def send_message(self, message: NetworkMessage):
        """Send message to server"""
        if not self.connected or not self.socket:
            return
        
        try:
            data = pickle.dumps(message)
            size = len(data)
            self.socket.sendall(size.to_bytes(4, 'big') + data)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
    
    def _receive_loop(self):
        """Receive messages from server"""
        while self.connected:
            try:
                message = self._receive_message()
                if message is None:
                    break
                
                self._process_message(message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break
        
        self.connected = False
    
    def _receive_message(self) -> Optional[NetworkMessage]:
        """Receive single message from server"""
        # Read size header
        size_data = self.socket.recv(4)
        if not size_data or len(size_data) < 4:
            return None
        
        size = int.from_bytes(size_data, 'big')
        
        # Read message data
        data = b''
        while len(data) < size:
            chunk = self.socket.recv(min(size - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        return pickle.loads(data)
    
    def _process_message(self, message: NetworkMessage):
        """Process incoming message"""
        with self.lock:
            if message.type == 'welcome':
                self.player_id = message.data['player_id']
                self.game_state = message.data['game_state']
                print(f"Assigned player ID: {self.player_id}")
                
            elif message.type == 'game_state':
                # Update full game state
                self.game_state = message.data
                
            # Trigger callbacks
            if message.type in self.message_callbacks:
                for callback in self.message_callbacks[message.type]:
                    callback(message.data)
    
    def register_callback(self, message_type: str, callback):
        """Register callback for specific message type"""
        if message_type not in self.message_callbacks:
            self.message_callbacks[message_type] = []
        self.message_callbacks[message_type].append(callback)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state (thread-safe)"""
        with self.lock:
            return self.game_state.copy()
