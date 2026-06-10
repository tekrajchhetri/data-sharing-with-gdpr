#!/usr/bin/env python3
"""
Querying demo
1. RSA encrypts symmetric keys
AES encrypts data deterministically
"""

from hybrid_encryption_system import HybridEncryptionSystem


def main():
    """Demonstrate symmetric encryption for direct querying."""
    
    # Initialize system with hybrid encryption
    system = HybridEncryptionSystem(
        num_layers=3,
        enable_hybrid=True,  # RSA for key management
        enable_query_indexing=True
    )
    
    # Sample data
    test_data = [
        b"gdprbookuser1@example.com",
        b"gdprbookuser2@example.com",
        b"gdprbookuser3@example.com",
        b"gdprbookusersupport@example.com"
    ]
    
    print("\n📋 Step 1: Encrypt Data with Hybrid System")
    print("-" * 40)
    
    encrypted_records = []
    for i, data in enumerate(test_data, 1):
        # Encrypt using hybrid system (RSA + AES)
        encrypted = system.encrypt(data)
        encrypted_records.append(encrypted)
        
        # Get final AES ciphertext (after RSA key management)
        num_layers = encrypted['metadata']['num_layers']
        final_ciphertext = encrypted[f'ciphertext_{num_layers+1}']
        
        print(f"Record {i}: {data.decode()}")
        print(f"  Final AES ciphertext: {final_ciphertext.hex()[:32]}...")
    
    print("\n📋 Step 2: Verify Deterministic Encryption")
    print("-" * 40)
    
    # Test that same input produces same output
    test_input = b"test@example.com"
    
    # Encrypt same data multiple times
    encrypted1 = system.encrypt(test_input)
    encrypted2 = system.encrypt(test_input)
    
    num_layers = encrypted1['metadata']['num_layers']
    ciphertext1 = encrypted1[f'ciphertext_{num_layers+1}']
    ciphertext2 = encrypted2[f'ciphertext_{num_layers+1}']
    
    print(f"Test data: {test_input.decode()}")
    print(f"First encryption:  {ciphertext1.hex()[:32]}...")
    print(f"Second encryption: {ciphertext2.hex()[:32]}...")
    print(f"Deterministic: {'✓ YES' if ciphertext1 == ciphertext2 else '✗ NO'}")
    
    print("\n📋 Step 3: Direct Query Using Encrypted Data")
    print("-" * 40)
    
    # Search terms
    search_terms = [
       b"gdprbookuser1@example.com",
        b"gdprbookuser2@example.com",
        b"gdprbookuser3@example.com",
    ]
    
    for search_term in search_terms:
        print(f"\nSearching for: {search_term.decode()}")
        
        # Encrypt search term using same process
        encrypted_search = system.encrypt_search_term(search_term, "email")
        print(f"Encrypted search: {encrypted_search.hex()[:32]}...")
        
        # Compare directly with stored encrypted data
        for i, encrypted_record in enumerate(encrypted_records, 1):
            num_layers = encrypted_record['metadata']['num_layers']
            stored_ciphertext = encrypted_record[f'ciphertext_{num_layers+1}']
            
            # Direct comparison - no extra indexes needed!
            is_match = encrypted_search == stored_ciphertext
            print(f"  Record {i}: {'✓ MATCH' if is_match else '✗ No match'}")
    
    print("\n📋 Step 4: Decrypt to Verify")
    print("-" * 40)
    
    # Decrypt all records to verify
    for i, encrypted_record in enumerate(encrypted_records, 1):
        decrypted = system.decrypt(encrypted_record)
        original = test_data[i-1]
        print(f"Verification Record {i}: {decrypted.decode()} (matches original: {decrypted == original})")
    
    print("\n📋 Step 5: Database Query Simulation")
    print("-" * 40)
    
    def find_by_email(email: bytes):
        """Simulate database query using encrypted search."""
        # Encrypt the search term
        encrypted_search = system.encrypt_search_term(email, "email")
        
        # Find matches by direct comparison
        matches = []
        for i, encrypted_record in enumerate(encrypted_records, 1):
            num_layers = encrypted_record['metadata']['num_layers']
            stored_ciphertext = encrypted_record[f'ciphertext_{num_layers+1}']
            
            if encrypted_search == stored_ciphertext:
                matches.append(i)
        
        return matches
    
    # Test queries
    test_queries = [
        b"gdprbookuser1@example.com",
        b"gdprbookuser2@example.com",
        b"gdprbookuser3@example.com",
        b"unknown@example.com"
    ]
    
    for query in test_queries:
        matches = find_by_email(query)
        print(f"Query '{query.decode()}': Found records {matches}")
     


if __name__ == "__main__":
    main() 