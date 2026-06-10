import os
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import json
from typing import Dict, List, Tuple, Optional, Union
import secrets
import struct


class HybridEncryptionSystem:
    """
    Enhanced Multi-Stage Hybrid Encryption System for Data Protection by Design

    This implementation is based on 

    Chhetri, T.R., Kurteva, A., DeLong, R.J., Hilscher, R., Korte, K. and Fensel, A., 2022. Data protection by design tool for automated GDPR compliance verification based on semantically modeled informed consent. Sensors, 22(7), p.2763.
    
    Features:
    - Hybrid encryption (symmetric + asymmetric)
    - Deterministic layered encryption for secure database querying
    - Dynamic configurable security levels
    - Support for secure querying over encrypted data
    - Flexible layer configuration
    """
    
    def __init__(self, 
                 master_key: Optional[bytes] = None,
                 key_size: int = 2048,
                 num_layers: int = 3,
                 layer_config: Optional[Dict[str, Dict]] = None,
                 enable_hybrid: bool = True,
                 enable_query_indexing: bool = True):
        """
        Initialize the hybrid encryption system with dynamic configuration.
        
        Args:
            master_key: Master key for symmetric encryption. If None, generates a random one.
            key_size: RSA key size in bits (default: 2048)
            num_layers: Number of encryption layers (1-10, default: 3)
            layer_config: Custom configuration for each layer
            enable_hybrid: Whether to use hybrid encryption (default: True)
            enable_query_indexing: Whether to enable query indexing (default: True)
        """
        if master_key is None:
            self.master_key = secrets.token_bytes(32)
        else:
            self.master_key = master_key
        
        self.num_layers = max(1, min(10, num_layers))
        self.key_size = key_size
        self.enable_hybrid = enable_hybrid
        self.enable_query_indexing = enable_query_indexing
        
        # Generate RSA key pair for asymmetric encryption (if hybrid is enabled)
        if self.enable_hybrid:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = None
            self.public_key = None
        
        # Generate symmetric keys for layered encryption
        self.layer_keys = self._generate_layer_keys()
        
        # Generate deterministic query keys for database operations
        if self.enable_query_indexing:
            self.query_keys = self._generate_query_keys()
        else:
            self.query_keys = {}
        
        # Apply custom layer configuration if provided
        if layer_config:
            self._apply_layer_config(layer_config)
    
    def _generate_layer_keys(self) -> Dict[str, bytes]:
        """Generate symmetric keys for each encryption layer."""
        keys = {}
        for i in range(1, self.num_layers + 1):
            keys[f'layer_{i}'] = secrets.token_bytes(32)
        return keys
    
    def _generate_query_keys(self) -> Dict[str, bytes]:
        """Generate deterministic keys for database querying."""
        # Use deterministic key derivation for query operations
        query_master = hashlib.sha256(self.master_key).digest()
        
        keys = {}
        for i in range(1, self.num_layers + 1):
            # Deterministic key derivation for consistent querying
            key_material = query_master + struct.pack('>I', i)
            keys[f'query_layer_{i}'] = hashlib.sha256(key_material).digest()
        return keys
    
    def _apply_layer_config(self, layer_config: Dict[str, Dict]):
        """Apply custom configuration to encryption layers."""
        for layer_id, config in layer_config.items():
            if layer_id in self.layer_keys:
                # Apply custom key if provided
                if 'custom_key' in config:
                    self.layer_keys[layer_id] = config['custom_key']
                
                # Apply custom algorithm if provided
                if 'algorithm' in config:
                    # Store algorithm preference for this layer
                    if not hasattr(self, 'layer_algorithms'):
                        self.layer_algorithms = {}
                    self.layer_algorithms[layer_id] = config['algorithm']
    
    def add_layer(self, layer_id: int, custom_key: Optional[bytes] = None):
        """Dynamically add a new encryption layer."""
        if layer_id <= self.num_layers:
            raise ValueError(f"Layer {layer_id} already exists")
        
        # Generate key for new layer
        if custom_key is None:
            custom_key = secrets.token_bytes(32)
        
        self.layer_keys[f'layer_{layer_id}'] = custom_key
        
        # Update number of layers
        self.num_layers = max(self.num_layers, layer_id)
        
        # Add query key if query indexing is enabled
        if self.enable_query_indexing:
            query_master = hashlib.sha256(self.master_key).digest()
            key_material = query_master + struct.pack('>I', layer_id)
            self.query_keys[f'query_layer_{layer_id}'] = hashlib.sha256(key_material).digest()
    
    def remove_layer(self, layer_id: int):
        """Dynamically remove an encryption layer."""
        if layer_id not in range(1, self.num_layers + 1):
            raise ValueError(f"Layer {layer_id} does not exist")
        
        # Remove layer key
        layer_key = f'layer_{layer_id}'
        if layer_key in self.layer_keys:
            del self.layer_keys[layer_key]
        
        # Remove query key
        query_key = f'query_layer_{layer_id}'
        if query_key in self.query_keys:
            del self.query_keys[query_key]
        
        # Update number of layers
        self.num_layers = max(1, self.num_layers - 1)
        
        # Renumber remaining layers if necessary
        self._renumber_layers()
    
    def _renumber_layers(self):
        """Renumber layers after removal to maintain sequential numbering."""
        old_keys = list(self.layer_keys.keys())
        old_query_keys = list(self.query_keys.keys())
        
        # Create new layer keys with sequential numbering
        new_layer_keys = {}
        new_query_keys = {}
        
        for i, old_key in enumerate(sorted(old_keys), 1):
            new_key = f'layer_{i}'
            new_layer_keys[new_key] = self.layer_keys[old_key]
            
            # Update query keys
            old_query_key = f'query_layer_{old_key.split("_")[1]}'
            if old_query_key in self.query_keys:
                new_query_key = f'query_layer_{i}'
                new_query_keys[new_query_key] = self.query_keys[old_query_key]
        
        self.layer_keys = new_layer_keys
        self.query_keys = new_query_keys
    
    def _hybrid_encrypt(self, data: bytes) -> bytes:
        """
        Hybrid encryption: Encrypt data with symmetric key, then encrypt the key with asymmetric encryption.
        """
        # Generate a random symmetric key for this encryption
        session_key = secrets.token_bytes(32)
        
        # Encrypt data with symmetric encryption (AES-256-GCM)
        iv = secrets.token_bytes(12)
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Encrypt the session key with RSA
        encrypted_session_key = self.public_key.encrypt(
            session_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine: encrypted session key + IV + ciphertext + tag
        return encrypted_session_key + iv + ciphertext + encryptor.tag
    
    def _hybrid_decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Hybrid decryption: Decrypt session key with private key, then decrypt data with session key.
        """
        # Extract components
        key_size = self.private_key.key_size // 8
        encrypted_session_key = encrypted_data[:key_size]
        iv = encrypted_data[key_size:key_size+12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[key_size+12:-16]
        
        # Decrypt session key with private key
        session_key = self.private_key.decrypt(
            encrypted_session_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt data with session key
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _deterministic_encrypt(self, data: bytes, key: bytes, layer_id: int) -> bytes:
        """
        Deterministic encryption for secure database querying.
        Uses deterministic IV based on data hash and layer ID.
        """
        # Create deterministic IV from data hash and layer ID
        data_hash = hashlib.sha256(data).digest()
        layer_bytes = struct.pack('>I', layer_id)
        iv_material = data_hash + layer_bytes + key[:8]
        iv = hashlib.sha256(iv_material).digest()[:16]
        
        # Encrypt with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + ciphertext
        return iv + ciphertext
    
    def _deterministic_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Deterministic decryption for secure database querying.
        """
        # Extract IV from the beginning of encrypted data
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Decrypt with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    def encrypt(self, data: bytes, use_hybrid: Optional[bool] = None) -> Dict[str, bytes]:
        """
        Perform the complete hybrid multi-stage encryption process.
        
        Args:
            data: Data to encrypt
            use_hybrid: Whether to use hybrid encryption for key management (defaults to system setting)
            
        Returns:
            Dictionary containing all ciphertexts and metadata
        """
        if use_hybrid is None:
            use_hybrid = self.enable_hybrid
            
        print("=== HYBRID ENCRYPTION PROCESS ===")
        
        # Phase 1: Key Management with Hybrid Encryption 
        
        # Encrypt layer keys using hybrid encryption
        layer_keys_bytes = json.dumps(self.layer_keys, default=lambda x: x.hex()).encode()
        
        if use_hybrid and self.enable_hybrid:
            ciphertext_1 = self._hybrid_encrypt(layer_keys_bytes) 
        else:
            # Fallback to symmetric encryption
            ciphertext_1 = self._symmetric_encrypt(layer_keys_bytes) 
        
        # Decrypt keys for use in layered encryption
        if use_hybrid and self.enable_hybrid:
            decrypted_keys_bytes = self._hybrid_decrypt(ciphertext_1)
        else:
            decrypted_keys_bytes = self._symmetric_decrypt(ciphertext_1)
        
        decrypted_keys = json.loads(decrypted_keys_bytes.decode())
        decrypted_layer_keys = {k: bytes.fromhex(v) for k, v in decrypted_keys.items()} 
        
        # Phase 2: Deterministic Layered Encryption 
        
        current_data = data
        ciphertexts = {}
        
        # Apply layered encryption dynamically
        for layer in range(1, self.num_layers + 1):
            layer_key = decrypted_layer_keys[f'layer_{layer}']
            current_data = self._deterministic_encrypt(current_data, layer_key, layer)
            ciphertexts[f'ciphertext_{layer+1}'] = current_data 
        
        # Store metadata
        metadata = {
            'num_layers': self.num_layers,
            'hybrid_encryption': use_hybrid and self.enable_hybrid,
            'key_size': self.key_size,
            'data_length': len(data),
            'enable_query_indexing': self.enable_query_indexing
        }
        
        result = {
            'ciphertext_1': ciphertext_1,
            'metadata': metadata,
            **ciphertexts
        }
        
        print("#"*60)
        print(f"Encrypted data: {result}")
        print("#"*60)
        print("=== HYBRID ENCRYPTION COMPLETE ===")
        return result
    
    def decrypt(self, encrypted_data: Dict[str, bytes]) -> bytes:
        """
        Perform the complete hybrid multi-stage decryption process.
        
        Args:
            encrypted_data: Dictionary containing ciphertexts and metadata
            
        Returns:
            Decrypted data
        """
        print("=== HYBRID DECRYPTION PROCESS ===")
        
        # Extract metadata
        metadata = encrypted_data.get('metadata', {})
        num_layers = metadata.get('num_layers', self.num_layers)
        use_hybrid = metadata.get('hybrid_encryption', self.enable_hybrid)
        
        
        # Phase 1: Key Decryption
        
        ciphertext_1 = encrypted_data['ciphertext_1']
        
        if use_hybrid and self.enable_hybrid:
            decrypted_keys_bytes = self._hybrid_decrypt(ciphertext_1) 
        else:
            decrypted_keys_bytes = self._symmetric_decrypt(ciphertext_1) 
        
        decrypted_keys = json.loads(decrypted_keys_bytes.decode())
        decrypted_layer_keys = {k: bytes.fromhex(v) for k, v in decrypted_keys.items()}
         
        
        # Start with the final ciphertext in the reverse order
        current_data = encrypted_data[f'ciphertext_{num_layers + 1}']
        
        # Decrypt in reverse order
        for layer in range(num_layers, 0, -1):
            layer_key = decrypted_layer_keys[f'layer_{layer}']
            current_data = self._deterministic_decrypt(current_data, layer_key) 
        
        print("=== HYBRID DECRYPTION COMPLETE ===")
        print("#"*60)
        print(f"Decrypted data: {current_data}")
        print("#"*60)
        return current_data
    
    def _symmetric_encrypt(self, data: bytes) -> bytes:
        """Fallback symmetric encryption for key management."""
        iv = secrets.token_bytes(12)
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv + ciphertext + encryptor.tag
    
    def _symmetric_decrypt(self, encrypted_data: bytes) -> bytes:
        """Fallback symmetric decryption for key management."""
        iv = encrypted_data[:12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[12:-16]
        
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def create_query_index(self, data: bytes, field_name: str) -> bytes:
        """
        Create a deterministic query index for secure database querying.
        This allows querying encrypted data without decryption.
        """
        # Create deterministic hash for querying
        query_key = self.query_keys['query_layer_1']
        field_hash = hashlib.sha256(field_name.encode()).digest()
        
        # Create deterministic index
        index_material = data + field_hash + query_key
        query_index = hashlib.sha256(index_material).digest()
        
        return query_index
    
    def search_encrypted_data(self, encrypted_data: bytes, search_term: bytes, field_name: str) -> bool:
        """
        Search encrypted data using deterministic encryption.
        Returns True if the search term matches the encrypted data.
        """
        # For deterministic encryption, we need to encrypt the search term
        # and compare it directly with the stored encrypted data
        
        # First, we need to decrypt the layer keys to encrypt the search term
        # This is a limitation - we need the keys to perform the search
        # In a real system, you might store the encrypted search terms separately
        
        # For now, let's create a simple deterministic hash comparison
        # This is not as secure as full deterministic encryption but demonstrates the concept
        
        # Create deterministic hash for search term
        search_hash = hashlib.sha256(search_term + field_name.encode()).digest()
        
        # Create deterministic hash for encrypted data
        data_hash = hashlib.sha256(encrypted_data + field_name.encode()).digest()
        
        return search_hash == data_hash
    
    def encrypt_search_term(self, search_term: bytes, field_name: str) -> bytes:
        """
        Encrypt a search term using the same deterministic encryption process.
        This allows searching encrypted data by encrypting the search term.
        """
        # Use the same deterministic encryption as the data
        current_data = search_term
        
        # Apply the same layered encryption process
        for layer in range(1, self.num_layers + 1):
            layer_key = self.layer_keys[f'layer_{layer}']
            current_data = self._deterministic_encrypt(current_data, layer_key, layer)
        
        return current_data
    
    def search_by_encryption(self, encrypted_data: bytes, search_term: bytes, field_name: str) -> bool:
        """
        Search encrypted data by encrypting the search term and comparing.
        This is the proper way to search deterministically encrypted data.
        """
        # Encrypt the search term using the same process
        encrypted_search_term = self.encrypt_search_term(search_term, field_name)
        
        # Compare the encrypted search term with the stored encrypted data
        return encrypted_search_term == encrypted_data
    
    def create_searchable_index(self, plaintext_data: bytes, field_name: str) -> bytes:
        """
        Create a searchable index from plaintext data.
        This index can be stored alongside encrypted data for searching.
        """
        return self.create_query_index(plaintext_data, field_name)
    
    def search_by_index(self, search_term: bytes, stored_index: bytes, field_name: str) -> bool:
        """
        Search using a pre-computed index.
        This is the correct way to search encrypted data.
        """
        search_index = self.create_query_index(search_term, field_name)
        return search_index == stored_index
    
    def get_public_key_pem(self) -> str:
        """Export public key in PEM format."""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    def get_private_key_pem(self) -> str:
        """Export private key in PEM format."""
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode()
    
    def export_keys(self) -> Dict[str, Union[bytes, str]]:
        """Export all keys for external use."""
        result = {
            'master_key': self.master_key,
            'layer_keys': self.layer_keys,
            'query_keys': self.query_keys,
            'num_layers': self.num_layers,
            'key_size': self.key_size,
            'enable_hybrid': self.enable_hybrid,
            'enable_query_indexing': self.enable_query_indexing
        }
        
        if self.enable_hybrid:
            result['public_key_pem'] = self.get_public_key_pem()
            result['private_key_pem'] = self.get_private_key_pem()
        
        return result
    
    def get_configuration(self) -> Dict[str, any]:
        """Get current system configuration."""
        return {
            'num_layers': self.num_layers,
            'key_size': self.key_size,
            'enable_hybrid': self.enable_hybrid,
            'enable_query_indexing': self.enable_query_indexing,
            'layer_keys_count': len(self.layer_keys),
            'query_keys_count': len(self.query_keys)
        }
    
    def update_configuration(self, **kwargs):
        """Update system configuration dynamically."""
        if 'num_layers' in kwargs:
            new_layers = kwargs['num_layers']
            if new_layers > self.num_layers:
                # Add new layers
                for i in range(self.num_layers + 1, new_layers + 1):
                    self.add_layer(i)
            elif new_layers < self.num_layers:
                # Remove excess layers
                for i in range(self.num_layers, new_layers, -1):
                    self.remove_layer(i)
        
        if 'enable_hybrid' in kwargs:
            self.enable_hybrid = kwargs['enable_hybrid']
            if self.enable_hybrid and self.private_key is None:
                # Generate RSA keys if hybrid is enabled
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=self.key_size,
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()
        
        if 'enable_query_indexing' in kwargs:
            self.enable_query_indexing = kwargs['enable_query_indexing']
            if self.enable_query_indexing and not self.query_keys:
                self.query_keys = self._generate_query_keys()
            elif not self.enable_query_indexing:
                self.query_keys = {}
    
    def get_layer_info(self) -> Dict[str, Dict]:
        """Get information about each encryption layer."""
        layer_info = {}
        for i in range(1, self.num_layers + 1):
            layer_key = f'layer_{i}'
            layer_info[layer_key] = {
                'key_length': len(self.layer_keys[layer_key]),
                'algorithm': 'AES-256-CBC',
                'deterministic': True
            }
            
            if self.enable_query_indexing:
                query_key = f'query_layer_{i}'
                if query_key in self.query_keys:
                    layer_info[layer_key]['query_indexing'] = True
                    layer_info[layer_key]['query_key_length'] = len(self.query_keys[query_key])
        
        return layer_info
