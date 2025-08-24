"""
FlowStack DataVault - Persistent Storage Client

Provides zero-config persistent storage for agents using MongoDB backend.
"""

import requests
import json
import uuid
from typing import Dict, List, Any, Optional, Union
from .exceptions import FlowStackError


class DataVault:
    """
    DataVault provides persistent storage for FlowStack customers.
    
    Each customer gets their own completely isolated MongoDB database.
    All data is automatically namespaced and secured per customer.
    Supports MongoDB-style queries and operations.
    
    Database naming: flowstack_{customer_id[:8]}_vault
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.flowstack.fun"):
        """
        Initialize DataVault client.
        
        Args:
            api_key: FlowStack API key for authentication
            base_url: Base URL for FlowStack API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.vault_url = f"{self.base_url}/datavault"
        
        # Headers for all requests
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'FlowStack-SDK/1.0.0'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to DataVault API."""
        url = f"{self.vault_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            else:
                response = requests.request(
                    method.upper(), 
                    url, 
                    headers=self.headers, 
                    json=data
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', str(e))
                except:
                    error_msg = f"DataVault error: {e.response.status_code} {e.response.reason}"
            else:
                error_msg = f"DataVault connection error: {str(e)}"
            
            raise FlowStackError(error_msg, error_code="DATAVAULT_ERROR")
    
    def store(self, collection: str, data: Dict[str, Any], key: Optional[str] = None) -> str:
        """
        Store data in a collection.
        
        Args:
            collection: Collection name (e.g., 'users', 'sessions')
            data: Dictionary of data to store
            key: Optional custom key (auto-generated if not provided)
        
        Returns:
            The key of the stored item
            
        Example:
            key = vault.store('users', {'name': 'Alice', 'age': 30})
            vault.store('users', {'name': 'Bob'}, key='user_bob')
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Generate key if not provided
        if key is None:
            key = f"{collection}_{uuid.uuid4().hex[:12]}"
        
        request_data = {
            'collection': collection,
            'key': key,
            'data': data,
            'operation': 'store'
        }
        
        result = self._make_request('POST', '', request_data)
        return result.get('key', key)
    
    def retrieve(self, collection: str, key: Optional[str] = None, 
                filter: Optional[Dict[str, Any]] = None) -> Union[Dict, List[Dict], None]:
        """
        Retrieve data from a collection.
        
        Args:
            collection: Collection name
            key: Specific key to retrieve (returns single item)
            filter: MongoDB-style query filter (returns list of items)
        
        Returns:
            Single dict if key provided, list of dicts if filter provided, None if not found
            
        Example:
            user = vault.retrieve('users', key='user_123')
            adults = vault.retrieve('users', filter={'age': {'$gte': 18}})
            all_users = vault.retrieve('users')  # Get all items
        """
        params = {
            'collection': collection,
            'operation': 'retrieve'
        }
        
        if key:
            params['key'] = key
        elif filter:
            params['filter'] = json.dumps(filter)
        
        result = self._make_request('GET', '', params)
        
        if key:
            # Single item retrieval
            items = result.get('data', [])
            return items[0] if items else None
        else:
            # Multiple items or all items
            return result.get('data', [])
    
    def query(self, collection: str, filter: Dict[str, Any]) -> List[Dict]:
        """
        Query data with MongoDB-style filters.
        
        Args:
            collection: Collection name
            filter: MongoDB-style query filter
        
        Returns:
            List of matching documents
            
        Example:
            adults = vault.query('users', {'age': {'$gte': 18}})
            active_users = vault.query('users', {'active': True, 'role': 'admin'})
        """
        return self.retrieve(collection, filter=filter) or []
    
    def update(self, collection: str, key: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing item.
        
        Args:
            collection: Collection name
            key: Key of item to update
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False if item not found
            
        Example:
            success = vault.update('users', 'user_123', {'age': 31, 'active': True})
        """
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary")
        
        request_data = {
            'collection': collection,
            'key': key,
            'updates': updates,
            'operation': 'update'
        }
        
        result = self._make_request('PUT', '', request_data)
        return result.get('success', False)
    
    def delete(self, collection: str, key: str) -> bool:
        """
        Delete an item from a collection.
        
        Args:
            collection: Collection name
            key: Key of item to delete
        
        Returns:
            True if deleted, False if not found
            
        Example:
            deleted = vault.delete('users', 'user_123')
        """
        request_data = {
            'collection': collection,
            'key': key,
            'operation': 'delete'
        }
        
        result = self._make_request('DELETE', '', request_data)
        return result.get('success', False)
    
    def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection: Collection name
            filter: Optional MongoDB-style query filter
        
        Returns:
            Number of matching documents
            
        Example:
            total_users = vault.count('users')
            active_users = vault.count('users', {'active': True})
        """
        params = {
            'collection': collection,
            'operation': 'count'
        }
        
        if filter:
            params['filter'] = json.dumps(filter)
        
        result = self._make_request('GET', '', params)
        return result.get('count', 0)
    
    def list_collections(self) -> List[str]:
        """
        List all collections in your isolated database.
        
        Only shows collections belonging to your customer account.
        Other customers' collections are never visible.
        
        Returns:
            List of collection names in your database
            
        Example:
            collections = vault.list_collections()  # ['users', 'sessions', 'memories']
        """
        result = self._make_request('GET', 'collections')
        
        # Collections from your customer's isolated database
        all_collections = result.get('collections', [])
        
        # Collections are namespaced, but we return the clean names to users
        # The API handles the database isolation internally
        unique_collections = set()
        for collection in all_collections:
            # Extract collection name after namespace prefix (format: "namespace_collection")
            if '_' in collection:
                collection_name = '_'.join(collection.split('_')[1:])
                if collection_name:
                    unique_collections.add(collection_name)
        
        return sorted(list(unique_collections))
    
    def clear(self, collection: str) -> bool:
        """
        Clear all items from a collection (use with caution).
        
        Args:
            collection: Collection name to clear
        
        Returns:
            True if successful
            
        Example:
            vault.clear('temp_cache')  # Removes all items from temp_cache collection
        """
        request_data = {
            'collection': collection,
            'operation': 'clear'
        }
        
        result = self._make_request('DELETE', '', request_data)
        return result.get('success', False)
    
    def health(self) -> Dict[str, Any]:
        """
        Check DataVault service health.
        
        Returns:
            Health status information
        """
        return self._make_request('GET', 'health')