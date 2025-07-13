#!/usr/bin/env python3
"""
Test Azure Blob Storage Integration
Verifies that the storage account and container are properly configured
"""

import os
import sys
from datetime import datetime

try:
    from azure.storage.blob import BlobServiceClient
    print("✅ Azure storage dependencies available")
except ImportError:
    print("❌ Azure storage dependencies not installed")
    print("Run: pip install azure-storage-blob")
    sys.exit(1)

def test_azure_storage():
    """Test Azure Blob Storage connection and upload"""
    
    # Load connection string
    connection_string = None
    try:
        with open('azure_storage_connection.txt', 'r') as f:
            connection_string = f.read().strip()
        print("✅ Connection string loaded")
    except FileNotFoundError:
        print("❌ azure_storage_connection.txt not found")
        return False
    
    if not connection_string or 'AccountKey=' not in connection_string:
        print("❌ Invalid connection string")
        return False
    
    try:
        # Initialize blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("✅ Blob service client initialized")
        
        # Test container access
        container_name = "music-files"
        container_client = blob_service_client.get_container_client(container_name)
        
        # Test container exists
        container_properties = container_client.get_container_properties()
        print(f"✅ Container '{container_name}' accessible")
        print(f"   Created: {container_properties.last_modified}")
        print(f"   Public Access: {container_properties.public_access}")
        
        # Test blob upload
        test_content = f"Azure storage test at {datetime.now()}"
        blob_name = "test-connection.txt"
        
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(test_content, overwrite=True)
        print(f"✅ Test blob uploaded: {blob_name}")
        
        # Generate public URL
        account_name = blob_service_client.account_name
        blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        print(f"✅ Public URL: {blob_url}")
        
        # Test blob download
        downloaded_content = blob_client.download_blob().readall().decode('utf-8')
        if downloaded_content == test_content:
            print("✅ Blob download verified")
        else:
            print("❌ Blob content mismatch")
            return False
        
        # Clean up test blob
        blob_client.delete_blob()
        print("✅ Test blob cleaned up")
        
        print("\n🎉 Azure Blob Storage test completed successfully!")
        print(f"📋 Storage Account: {account_name}")
        print(f"📦 Container: {container_name}")
        print(f"🌐 Base URL: https://{account_name}.blob.core.windows.net/{container_name}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure storage test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Azure Blob Storage Integration...")
    print("=" * 50)
    
    success = test_azure_storage()
    
    if success:
        print("\n✅ Azure storage is ready for the AI music generator!")
        print("\nNext steps:")
        print("1. Deploy backend with: python app_enhanced_ai_azure.py")
        print("2. Set AZURE_STORAGE_CONNECTION_STRING environment variable")
        print("3. Test music generation with Azure storage")
    else:
        print("\n❌ Azure storage test failed")
        print("Please check your configuration and try again")
        sys.exit(1)
