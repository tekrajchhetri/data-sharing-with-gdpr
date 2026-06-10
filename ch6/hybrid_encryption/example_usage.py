#!/usr/bin/env python3
"""
Dynamic Configuration Example for Hybrid Encryption System
Demonstrates basic dynamic configuration features.
"""

from hybrid_encryption_system import HybridEncryptionSystem
import time


def main():
    """Demonstrate basic dynamic configuration features."""
    
    print("Dynamic Hybrid Encryption System - Basic Examples")
    print("=" * 60)
    
    # Test 1: Basic dynamic setup and encryption
    print("\npythTest 1: Basic Dynamic Setup")
    print("-" * 40)
    
    # Initialize with custom configuration
    system = HybridEncryptionSystem(
        num_layers=3,
        enable_hybrid=True,
        enable_query_indexing=True
    )
    
    print("Initial Configuration:")
    config = system.get_configuration()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Test data
    test_data = b"This is a test message for dynamic configuration!"
    print(f"\nOriginal data: {test_data.decode()}")
    
    # Encrypt with current configuration
    encrypted_result = system.encrypt(test_data)
    print(f"Encrypted with {encrypted_result['metadata']['num_layers']} layers")
    
    # Decrypt
    decrypted_data = system.decrypt(encrypted_result)
    print(f"Decrypted data: {decrypted_data.decode()}")
    print(f"Success: {test_data == decrypted_data}")
    
    # Test 2: Dynamic layer management
    print("\n📋 Test 2: Dynamic Layer Management")
    print("-" * 40)
    
    # Add a new layer
    print("Adding layer 4...")
    system.add_layer(4)
    
    # Add another layer with custom key
    custom_key = b"custom_key_for_layer_5_32_bytes_long"[:32]
    print(f"Adding layer 5 with custom key (length: {len(custom_key)} bytes)...")
    system.add_layer(5, custom_key)
    
    print(f"Updated configuration: {system.get_configuration()}")
    
    # Show layer information
    layer_info = system.get_layer_info()
    print("\nLayer Information:")
    for layer, info in layer_info.items():
        print(f"  {layer}: {info}")
    
    # Test encryption with more layers
    encrypted_result_2 = system.encrypt(test_data)
    decrypted_data_2 = system.decrypt(encrypted_result_2)
    print(f"\nEncryption with {encrypted_result_2['metadata']['num_layers']} layers successful: {test_data == decrypted_data_2}")
    
    # Test 3: Dynamic configuration updates
    print("\n📋 Test 3: Dynamic Configuration Updates")
    print("-" * 40)
    
    # Update multiple settings at once
    system.update_configuration(
        num_layers=6,
        enable_hybrid=False,
        enable_query_indexing=True
    )
    
    print("After configuration update:")
    config = system.get_configuration()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Test encryption with new configuration
    encrypted_result_3 = system.encrypt(test_data)
    decrypted_data_3 = system.decrypt(encrypted_result_3)
    print(f"Encryption with new config successful: {test_data == decrypted_data_3}")
    
    # Test 4: Performance comparison
    print("\nTest 4: Performance Comparison")
    print("-" * 40)
    
    # Test different layer configurations
    layer_configs = [1, 3, 5, 7]
    
    for num_layers in layer_configs:
        system = HybridEncryptionSystem(num_layers=num_layers, enable_hybrid=False)
        
        start_time = time.time()
        encrypted = system.encrypt(test_data)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted = system.decrypt(encrypted)
        decrypt_time = time.time() - start_time
        
        success = test_data == decrypted
        
        print(f"{num_layers:2d} layers: "
              f"Encrypt: {encrypt_time*1000:6.2f}ms, "
              f"Decrypt: {decrypt_time*1000:6.2f}ms, "
              f"Success: {'✓' if success else '✗'}")
    
    print("\n Dynamic configuration demonstration completed!")


if __name__ == "__main__":
    main() 