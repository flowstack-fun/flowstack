# DataVault - Zero-Config Persistence

Every FlowStack agent gets persistent storage with zero configuration. No database setup, no connection strings, no migrations. Just store and retrieve data.

## What is DataVault?

**DataVault** is MongoDB-backed storage that's automatically created for each customer. Each customer gets their own completely isolated database, ensuring total data privacy and security. Think of it as a simple database that just works - with enterprise-grade isolation.

```python
# Store data
agent.vault.store('users', {'name': 'Alice', 'age': 30})

# Retrieve data  
user = agent.vault.retrieve('users', key='user_123')

# Query data
adults = agent.vault.query('users', {'age': {'$gte': 18}})
```

## Core Operations

### Store Data

Store any JSON-serializable data in named collections:

```python
# Store with auto-generated key
key = agent.vault.store('products', {
    'name': 'Laptop',
    'price': 999.99,
    'category': 'electronics'
})
print(key)  # → "prod_abc123def456"

# Store with custom key
agent.vault.store('products', {
    'name': 'Mouse',
    'price': 29.99,
    'category': 'electronics'
}, key='mouse-001')
```

### Retrieve Data

Get data back using keys or queries:

```python
# Get by key
product = agent.vault.retrieve('products', key='mouse-001')
print(product['name'])  # → "Mouse"

# Get all items in collection
all_products = agent.vault.retrieve('products')
print(f"Found {len(all_products)} products")

# Query with filters
expensive_items = agent.vault.query('products', {
    'price': {'$gte': 500}
})
```

### Update Data

Modify existing items:

```python
# Update specific fields
success = agent.vault.update('products', 'mouse-001', {
    'price': 24.99,
    'sale': True
})

# Or retrieve, modify, and store back
product = agent.vault.retrieve('products', key='mouse-001')
product['price'] = 19.99
agent.vault.store('products', product, key='mouse-001')
```

### Delete Data

Remove items you no longer need:

```python
# Delete specific item
agent.vault.delete('products', key='mouse-001')

# Clear entire collection (be careful!)
agent.vault.clear('products')
```

## Collections as Namespaces

Organize your data using **collections** - like database tables:

```python
# User data
agent.vault.store('users', {
    'id': 'user_123',
    'name': 'Alice Johnson',
    'email': 'alice@example.com',
    'preferences': {
        'theme': 'dark',
        'notifications': True,
        'language': 'en'
    }
})

# Conversation history
agent.vault.store('conversations', {
    'user_id': 'user_123',
    'messages': [
        {'role': 'user', 'content': 'Hello!'},
        {'role': 'assistant', 'content': 'Hi! How can I help?'}
    ],
    'started_at': '2024-01-15T10:00:00Z',
    'last_activity': '2024-01-15T10:05:00Z'
})

# Application state
agent.vault.store('app_state', {
    'last_backup': '2024-01-15T00:00:00Z',
    'feature_flags': {
        'beta_features': True,
        'advanced_mode': False
    },
    'metrics': {
        'total_users': 1250,
        'active_sessions': 45
    }
})
```

## Query Patterns

DataVault supports MongoDB-style queries for complex data retrieval:

### Basic Queries

```python
# Exact match
users_named_alice = agent.vault.query('users', {'name': 'Alice Johnson'})

# Multiple conditions (AND)
young_adults = agent.vault.query('users', {
    'age': {'$gte': 18, '$lt': 30},
    'active': True
})

# OR conditions
power_users = agent.vault.query('users', {
    '$or': [
        {'premium': True},
        {'login_count': {'$gte': 100}}
    ]
})
```

### Advanced Queries

```python
# Text search
search_results = agent.vault.query('products', {
    'name': {'$regex': 'laptop', '$options': 'i'}  # Case-insensitive
})

# Array queries
electronics = agent.vault.query('products', {
    'categories': {'$in': ['electronics', 'computers']}
})

# Nested field queries
dark_theme_users = agent.vault.query('users', {
    'preferences.theme': 'dark'
})

# Query with multiple conditions
user_conversations = agent.vault.query('conversations', {
    'user_id': 'user_123',
    'active': True
})
```

### Aggregation

Count and analyze your data:

```python
# Count items
total_users = agent.vault.count('users')
active_users = agent.vault.count('users', {'active': True})

# List all collections - only shows your collections
collections = agent.vault.list_collections()
print(f"Your collections: {collections}")  # Only collections in your isolated database
```

## Real-World Examples

### E-commerce Shopping Cart

```python
@agent.tool
def add_to_cart(user_id: str, product_id: str, quantity: int = 1):
    """Add item to user's shopping cart"""
    # Get existing cart or create new one
    cart = agent.vault.retrieve('carts', key=user_id) or {
        'user_id': user_id,
        'items': [],
        'total': 0.0,
        'created_at': datetime.now().isoformat()
    }
    
    # Get product details
    product = agent.vault.retrieve('products', key=product_id)
    if not product:
        return {'error': 'Product not found'}
    
    # Add or update item in cart
    for item in cart['items']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart['items'].append({
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        })
    
    # Recalculate total
    cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'])
    cart['updated_at'] = datetime.now().isoformat()
    
    # Save cart
    agent.vault.store('carts', cart, key=user_id)
    
    return {
        'message': f"Added {quantity}x {product['name']} to cart",
        'cart_total': cart['total'],
        'item_count': len(cart['items'])
    }

@agent.tool
def get_cart(user_id: str):
    """Get user's current shopping cart"""
    cart = agent.vault.retrieve('carts', key=user_id)
    if not cart:
        return {'message': 'Cart is empty', 'items': [], 'total': 0}
    
    return {
        'items': cart['items'],
        'total': cart['total'],
        'item_count': len(cart['items'])
    }
```

### Fitness Tracking

```python
@agent.tool
def log_workout(user_id: str, workout_type: str, duration: int, calories: int):
    """Log a workout session"""
    workout = {
        'user_id': user_id,
        'type': workout_type,
        'duration_minutes': duration,
        'calories_burned': calories,
        'date': datetime.now().date().isoformat(),
        'timestamp': datetime.now().isoformat()
    }
    
    # Store workout
    workout_key = agent.vault.store('workouts', workout)
    
    # Update user stats
    stats = agent.vault.retrieve('fitness_stats', key=user_id) or {
        'user_id': user_id,
        'total_workouts': 0,
        'total_duration': 0,
        'total_calories': 0,
        'favorite_activities': {},
        'streak_days': 0
    }
    
    stats['total_workouts'] += 1
    stats['total_duration'] += duration
    stats['total_calories'] += calories
    
    # Track favorite activities
    if workout_type not in stats['favorite_activities']:
        stats['favorite_activities'][workout_type] = 0
    stats['favorite_activities'][workout_type] += 1
    
    # Calculate streak (simplified)
    today = datetime.now().date()
    recent_workouts = agent.vault.query('workouts', {
        'user_id': user_id,
        'date': today.isoformat()
    })
    
    if len(recent_workouts) == 1:  # First workout today
        yesterday_workouts = agent.vault.query('workouts', {
            'user_id': user_id,
            'date': (today - timedelta(days=1)).isoformat()
        })
        if yesterday_workouts:
            stats['streak_days'] += 1
        else:
            stats['streak_days'] = 1
    
    agent.vault.store('fitness_stats', stats, key=user_id)
    
    return {
        'message': f'Logged {duration} min {workout_type} workout',
        'workout_id': workout_key,
        'total_workouts': stats['total_workouts'],
        'streak_days': stats['streak_days']
    }

@agent.tool
def get_fitness_summary(user_id: str, days: int = 7):
    """Get fitness summary for recent days"""
    start_date = (datetime.now().date() - timedelta(days=days)).isoformat()
    
    recent_workouts = agent.vault.query('workouts', {
        'user_id': user_id,
        'date': {'$gte': start_date}
    })
    
    stats = agent.vault.retrieve('fitness_stats', key=user_id) or {}
    
    summary = {
        'period_days': days,
        'workouts_this_period': len(recent_workouts),
        'total_duration': sum(w['duration_minutes'] for w in recent_workouts),
        'total_calories': sum(w['calories_burned'] for w in recent_workouts),
        'workout_types': list(set(w['type'] for w in recent_workouts)),
        'overall_stats': stats
    }
    
    return summary
```

### Customer Support Memory

```python
@agent.tool
def remember_customer_context(customer_id: str, context: str, category: str = "general"):
    """Remember important context about a customer"""
    memory = {
        'customer_id': customer_id,
        'context': context,
        'category': category,
        'timestamp': datetime.now().isoformat(),
        'agent_session': 'current'  # Track which conversation this came from
    }
    
    memory_key = agent.vault.store('customer_memory', memory)
    
    return {
        'message': f'Remembered: {context}',
        'memory_id': memory_key,
        'category': category
    }

@agent.tool
def recall_customer_context(customer_id: str, category: str = None):
    """Recall previous context about a customer"""
    query = {'customer_id': customer_id}
    if category:
        query['category'] = category
    
    memories = agent.vault.query('customer_memory', query)
    
    if not memories:
        return {'message': 'No previous context found for this customer'}
    
    context_summary = []
    for memory in memories:
        context_summary.append({
            'context': memory['context'],
            'category': memory['category'],
            'when': memory['timestamp']
        })
    
    return {
        'customer_id': customer_id,
        'context_items': len(memories),
        'contexts': context_summary
    }

@agent.tool
def search_customer_history(query: str):
    """Search across all customer interactions"""
    # Text search across customer memory
    results = agent.vault.query('customer_memory', {
        '$or': [
            {'context': {'$regex': query, '$options': 'i'}},
            {'category': {'$regex': query, '$options': 'i'}}
        ]
    })
    
    return {
        'query': query,
        'matches': len(results),
        'results': results[:5]  # Limit to top 5 matches
    }
```

## Performance Tips

### Efficient Queries

```python
# ✅ Good: Use indexes (key-based lookups are fastest)
user = agent.vault.retrieve('users', key='user_123')

# ✅ Good: Query with specific fields
recent_orders = agent.vault.query('orders', {
    'user_id': 'user_123',
    'status': 'completed',
    'created_at': {'$gte': '2024-01-01'}
})

# ⚠️ Slower: Querying without indexes
all_users = agent.vault.retrieve('users')  # Gets everything
expensive_search = agent.vault.query('products', {
    'description': {'$regex': 'bluetooth'}  # Text search across all descriptions
})
```

### Data Organization

```python
# ✅ Good: Organize related data together
user_profile = {
    'basic_info': {'name': 'Alice', 'email': 'alice@example.com'},
    'preferences': {'theme': 'dark', 'language': 'en'},
    'metadata': {'created_at': '2024-01-01', 'last_login': '2024-01-15'}
}

# ✅ Good: Use consistent key patterns
agent.vault.store('users', user_profile, key='user_123')
agent.vault.store('user_sessions', session_data, key='user_123_session_456')

# ⚠️ Less efficient: Storing everything separately
agent.vault.store('user_names', {'name': 'Alice'}, key='user_123')
agent.vault.store('user_emails', {'email': 'alice@example.com'}, key='user_123')
agent.vault.store('user_themes', {'theme': 'dark'}, key='user_123')
```

### Cleanup and Maintenance

```python
@agent.tool
def cleanup_old_data():
    """Clean up old data to save space"""
    from datetime import datetime, timedelta
    
    # Delete old conversation logs (older than 30 days)
    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    old_conversations = agent.vault.query('conversations', {
        'last_activity': {'$lt': cutoff_date}
    })
    
    deleted_count = 0
    for conv in old_conversations:
        agent.vault.delete('conversations', key=conv['_id'])
        deleted_count += 1
    
    return f"Cleaned up {deleted_count} old conversations"

@agent.tool
def get_storage_stats():
    """Get storage usage statistics"""
    collections = agent.vault.list_collections()
    stats = {}
    
    for collection in collections:
        count = agent.vault.count(collection)
        stats[collection] = count
    
    return {
        'collections': len(collections),
        'total_items': sum(stats.values()),
        'breakdown': stats
    }
```

## Best Practices

### ✅ Do

- **Use descriptive collection names**: `user_preferences` not `prefs`
- **Include timestamps**: Always add `created_at` and `updated_at` fields
- **Use consistent key patterns**: `user_123`, `session_user_123_456`
- **Store related data together**: Don't create unnecessary collections
- **Clean up old data**: Implement periodic cleanup to manage storage

### ❌ Don't

- **Store large files**: DataVault is for structured data, not media
- **Store secrets**: Use BYOK for API keys, not DataVault
- **Create too many collections**: Keep it organized but not over-fragmented
- **Ignore query performance**: Use specific queries, not broad searches
- **Store temporary data permanently**: Clean up session data and caches

### Security Considerations

- **Complete database isolation per customer** - each customer has their own MongoDB database
- **Zero cross-customer data access** - impossible to access another customer's data
- **Data is encrypted at rest** using industry-standard encryption
- **Automatic namespace isolation** - collections are scoped to your database only
- **Use for application data only** - not for user passwords or API keys

### Data Isolation Architecture

**Database Naming Convention:**
```
flowstack_{customer_id}_vault
```

**How It Works:**
1. When you first use DataVault, FlowStack creates a dedicated MongoDB database for your customer account
2. All your collections are stored in this isolated database
3. Your API key can only access your database - no other customer data is visible
4. `list_collections()` only returns collections from your database
5. All queries and operations are automatically scoped to your database

**Example Database Structure:**
```
MongoDB Cluster:
├── flowstack_abc12345_vault     # Customer A's database
│   ├── users                    # Customer A's users collection
│   ├── orders                   # Customer A's orders collection
│   └── sessions                 # Customer A's sessions collection
├── flowstack_def67890_vault     # Customer B's database
│   ├── products                 # Customer B's products collection
│   └── analytics                # Customer B's analytics collection
└── flowstack_ghi11223_vault     # Customer C's database
    └── conversations            # Customer C's conversations collection
```

This architecture ensures complete data privacy - it's impossible for one customer to access another's data, even by accident.

---

Ready to build something with persistent data? Check out our [recipes](recipes/stateful-agent.md) for complete examples, or learn about [deployment](deployment.md) to get your agent live!