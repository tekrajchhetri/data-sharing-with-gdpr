# Hybrid Encryption System for Data Protection by Design

This implementation provides an enhanced multi-stage hybrid encryption system that supports "data protection by design" principles with hybrid encryption (symmetric + asymmetric) and deterministic layered encryption to support secure database querying.

This implementation is based on the following article. 

Chhetri, T.R., Kurteva, A., DeLong, R.J., Hilscher, R., Korte, K. and Fensel, A., 2022. Data protection by design tool for automated GDPR compliance verification based on semantically modeled informed consent. Sensors, 22(7), p.2763.


## 🎯 Key Features

### Data Protection by Design
- **Hybrid Encryption**: Combines symmetric and asymmetric encryption for optimal security and performance
- **Deterministic Layered Encryption**: Enables secure querying of encrypted data in databases
- **Dynamic Configuration**: Runtime adjustment of encryption layers (1-10) and security features
- **Secure Database Querying**: Search encrypted data without decryption
- **Flexible Setup**: Custom layer configuration and key management

### Hybrid Encryption Architecture
- **Symmetric Encryption**: Fast encryption of bulk data using AES-256-GCM
- **Asymmetric Encryption**: Secure key exchange using RSA-2048 with OAEP padding
- **Layered Security**: Multiple encryption layers provide defense in depth
- **Deterministic Operations**: Consistent encryption for database querying

To learn more please refer to `Chhetri, T.R., Kurteva, A., DeLong, R.J., Hilscher, R., Korte, K. and Fensel, A., 2022. Data protection by design tool for automated GDPR compliance verification based on semantically modeled informed consent. Sensors, 22(7), p.2763.`

## 🏗️ System Architecture

### Phase 1: Hybrid Key Management
1. **Key Generation**: Generate RSA key pair and symmetric layer keys
2. **Hybrid Encryption**: Encrypt layer keys using hybrid approach
   - Encrypt data with random session key (AES-256-GCM)
   - Encrypt session key with RSA public key
3. **Key Storage**: Store encrypted keys securely

### Phase 2: Deterministic Layered Encryption
1. **Layer 1**: Encrypt data with deterministic AES-256-CBC
2. **Layer 2-N**: Apply additional encryption layers (dynamically configurable)
3. **Query Indexing**: Create deterministic indexes for database operations
4. **Dynamic Management**: Add/remove layers at runtime



## Description:

### Query Index Structure
- **Deterministic**: Same input produces same index
- **Field-Specific**: Different indexes for different fields
- **Collision Resistant**: SHA-256 based hashing
- **Privacy Preserving**: No information leakage

## 🔧 Configuration Options

### Dynamic Layer Configuration
- **1-10 Layers**: Configurable number of encryption layers
- **Runtime Adjustment**: Add/remove layers without reinitializing
- **Custom Keys**: Specify custom keys for individual layers
- **Performance Tuning**: Balance security vs. performance
- **Default**: 3 layers for optimal security/performance balance

### Key Sizes
- **RSA Keys**: 2048 bits (default), 4096 bits (high security)
- **AES Keys**: 256 bits for all symmetric operations
- **Session Keys**: 256 bits for hybrid encryption


## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Dynamic Configuration

```python
from encryption_system import HybridEncryptionSystem

# Initialize with dynamic configuration
system = HybridEncryptionSystem(
    num_layers=3,
    enable_hybrid=True,
    enable_query_indexing=True
)

# Encrypt data
data = b"Your sensitive data here"
encrypted_result = system.encrypt(data)

# Decrypt data
decrypted_data = system.decrypt(encrypted_result)
print(f"Decrypted: {decrypted_data.decode()}")
```

### Secure Database Querying

```python
# Create query indexes for database operations
email_field = "email"
user_email = b"user@example.com"

# Create deterministic query index
query_index = system.create_query_index(user_email, email_field)

# Search encrypted records
encrypted_record = b"encrypted_user_data"
is_match = system.search_encrypted_data(encrypted_record, user_email, email_field)
print(f"Match found: {is_match}")
```

### Dynamic Layer Management

```python
# Initialize system
system = HybridEncryptionSystem(num_layers=3)

# Add new layers dynamically
system.add_layer(4)
system.add_layer(5, custom_key=b"your_custom_key_32_bytes")

# Remove layers
system.remove_layer(5)

# Update configuration
system.update_configuration(
    num_layers=6,
    enable_hybrid=False,
    enable_query_indexing=True
)

# Get current configuration
config = system.get_configuration()
layer_info = system.get_layer_info()
```

### Advanced Configuration

```python
# Initialize with custom parameters
system = HybridEncryptionSystem(
    master_key=your_master_key,
    key_size=4096,  # Stronger RSA keys
    num_layers=5,   # Maximum security
    enable_hybrid=True,
    enable_query_indexing=True
)

# Custom layer configuration
custom_config = {
    'layer_1': {'custom_key': b'custom_key_1_32_bytes_long!'},
    'layer_2': {'custom_key': b'custom_key_2_32_bytes_long!'}
}

system = HybridEncryptionSystem(
    num_layers=2,
    layer_config=custom_config
)

# Export keys for external use
keys = system.export_keys()
public_key_pem = system.get_public_key_pem()
```



## 📄 License

This implementation is provided for educational and research purposes.  