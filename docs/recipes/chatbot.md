# Recipe: Intelligent Chatbot

Build a Slack bot that remembers conversations, learns user preferences, and integrates with your existing tools.

!!! tip "Perfect for Indie Hackers"
    This recipe shows how to build a production-ready chatbot in under an hour. Deploy it to Slack, Discord, or any chat platform.

## What You'll Build

A chatbot that can:

- 💬 **Remember conversations** across sessions
- 👤 **Learn user preferences** and adapt responses  
- 🔧 **Use custom tools** to perform actions
- 📊 **Track usage and analytics** automatically
- 🚀 **Scale to thousands of users** without infrastructure work

## The Complete Code

```python title="slack_bot.py"
from flowstack import Agent
from datetime import datetime, timedelta
import json

# Initialize the bot
bot = Agent(
    name="company-assistant",
    api_key="fs_your_api_key_here",
    system_prompt="""You are a helpful company assistant bot. You can help users with:
    - Checking their vacation days and time off
    - Looking up company policies and information  
    - Remembering their preferences for future conversations
    - Helping with common HR and workplace questions
    
    Always be friendly and professional. Use the available tools to provide accurate information."""
)

# Tool 1: Vacation Day Management
@bot.tool
def check_vacation_days(user_id: str) -> dict:
    """Check how many vacation days a user has remaining"""
    # In a real app, this would query your HR system
    # For demo, we'll use DataVault to simulate user data
    
    user_data = bot.vault.retrieve('employees', key=user_id) or {
        'user_id': user_id,
        'vacation_days_total': 20,
        'vacation_days_used': 0,
        'vacation_requests': []
    }
    
    remaining = user_data['vacation_days_total'] - user_data['vacation_days_used']
    
    return {
        'user_id': user_id,
        'total_days': user_data['vacation_days_total'],
        'used_days': user_data['vacation_days_used'],
        'remaining_days': remaining,
        'recent_requests': user_data['vacation_requests'][-3:]  # Last 3 requests
    }

@bot.tool
def request_vacation(user_id: str, start_date: str, end_date: str, reason: str = "") -> dict:
    """Submit a vacation request"""
    from datetime import datetime
    
    # Get user data
    user_data = bot.vault.retrieve('employees', key=user_id) or {
        'user_id': user_id,
        'vacation_days_total': 20,
        'vacation_days_used': 0,
        'vacation_requests': []
    }
    
    # Calculate days requested
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    days_requested = (end - start).days + 1
    
    # Check if enough days available
    remaining = user_data['vacation_days_total'] - user_data['vacation_days_used']
    if days_requested > remaining:
        return {
            'success': False,
            'message': f'Not enough vacation days. You have {remaining} days remaining, but requested {days_requested} days.'
        }
    
    # Create request
    request = {
        'id': f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'start_date': start_date,
        'end_date': end_date,
        'days': days_requested,
        'reason': reason,
        'status': 'pending',
        'submitted_at': datetime.now().isoformat()
    }
    
    # Update user data
    user_data['vacation_requests'].append(request)
    user_data['vacation_days_used'] += days_requested  # Optimistically reserve
    
    bot.vault.store('employees', user_data, key=user_id)
    
    # Store the request for HR review
    bot.vault.store('vacation_requests', request, key=request['id'])
    
    return {
        'success': True,
        'message': f'Vacation request submitted for {days_requested} days from {start_date} to {end_date}',
        'request_id': request['id'],
        'remaining_days': user_data['vacation_days_total'] - user_data['vacation_days_used']
    }

# Tool 2: Company Knowledge Base
@bot.tool
def search_company_policies(query: str) -> dict:
    """Search company policies and information"""
    # In a real app, this would search your knowledge base
    # For demo, we'll create some sample policies
    
    policies = [
        {
            'title': 'Remote Work Policy',
            'content': 'Employees can work remotely up to 3 days per week with manager approval.',
            'category': 'workplace',
            'tags': ['remote', 'work from home', 'flexible']
        },
        {
            'title': 'Vacation Policy', 
            'content': 'Full-time employees receive 20 vacation days per year. Part-time employees receive prorated vacation.',
            'category': 'time-off',
            'tags': ['vacation', 'time off', 'PTO']
        },
        {
            'title': 'Equipment Policy',
            'content': 'Company provides laptop and necessary equipment. Personal use is allowed within reason.',
            'category': 'equipment',
            'tags': ['laptop', 'equipment', 'IT']
        },
        {
            'title': 'Health Benefits',
            'content': 'Medical, dental, and vision coverage available. Company covers 80% of premiums.',
            'category': 'benefits',
            'tags': ['health', 'medical', 'benefits', 'insurance']
        }
    ]
    
    # Simple text search
    query_lower = query.lower()
    matching_policies = []
    
    for policy in policies:
        if (query_lower in policy['title'].lower() or 
            query_lower in policy['content'].lower() or
            any(query_lower in tag for tag in policy['tags'])):
            matching_policies.append(policy)
    
    return {
        'query': query,
        'matches': len(matching_policies),
        'policies': matching_policies
    }

# Tool 3: User Preference Management
@bot.tool
def remember_user_preference(user_id: str, preference_type: str, value: str) -> dict:
    """Remember a user's preference for future conversations"""
    
    # Get existing preferences
    prefs = bot.vault.retrieve('user_preferences', key=user_id) or {
        'user_id': user_id,
        'preferences': {},
        'updated_at': datetime.now().isoformat()
    }
    
    # Update preference
    prefs['preferences'][preference_type] = value
    prefs['updated_at'] = datetime.now().isoformat()
    
    # Store back
    bot.vault.store('user_preferences', prefs, key=user_id)
    
    return {
        'message': f"I'll remember that you prefer {preference_type}: {value}",
        'user_id': user_id,
        'preference_type': preference_type,
        'value': value
    }

@bot.tool
def get_user_preferences(user_id: str) -> dict:
    """Get a user's saved preferences"""
    
    prefs = bot.vault.retrieve('user_preferences', key=user_id)
    
    if not prefs:
        return {
            'user_id': user_id,
            'preferences': {},
            'message': 'No preferences saved yet'
        }
    
    return {
        'user_id': user_id,
        'preferences': prefs['preferences'],
        'last_updated': prefs['updated_at']
    }

# Tool 4: Conversation History
@bot.tool
def save_conversation_summary(user_id: str, summary: str, topics: list) -> dict:
    """Save a summary of the conversation for future reference"""
    
    conversation = {
        'user_id': user_id,
        'summary': summary,
        'topics': topics,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat()
    }
    
    # Store conversation
    conv_key = bot.vault.store('conversations', conversation)
    
    return {
        'message': 'Conversation summary saved',
        'conversation_id': conv_key,
        'topics': topics
    }

@bot.tool
def recall_previous_conversations(user_id: str, days_back: int = 7) -> dict:
    """Recall previous conversations with this user"""
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
    
    recent_conversations = bot.vault.query('conversations', {
        'user_id': user_id,
        'date': {'$gte': cutoff_date}
    }, sort=[('timestamp', -1)], limit=5)
    
    if not recent_conversations:
        return {
            'user_id': user_id,
            'conversations': [],
            'message': f'No conversations found in the last {days_back} days'
        }
    
    return {
        'user_id': user_id,
        'conversation_count': len(recent_conversations),
        'conversations': recent_conversations,
        'time_period': f'last {days_back} days'
    }

# Test the bot locally
def test_bot():
    """Test the bot with sample interactions"""
    print("🤖 Testing Company Assistant Bot")
    print("=" * 50)
    
    # Test vacation day check
    print("\n1. Checking vacation days...")
    response = bot.chat("How many vacation days do I have left? My user ID is emp_123")
    print(f"Bot: {response}")
    
    # Test preference setting
    print("\n2. Setting a preference...")
    response = bot.chat("Please remember that I prefer to be notified about meetings via email, not Slack. My user ID is emp_123")
    print(f"Bot: {response}")
    
    # Test policy search
    print("\n3. Searching company policies...")
    response = bot.chat("What's our remote work policy?")
    print(f"Bot: {response}")
    
    # Test vacation request
    print("\n4. Requesting vacation...")
    response = bot.chat("I'd like to request vacation from 2024-03-15 to 2024-03-18 for a family trip. My user ID is emp_123")
    print(f"Bot: {response}")
    
    print("\n✅ Local testing complete!")

# Deploy to production
def deploy_bot():
    """Deploy the bot to production"""
    print("\n🚀 Deploying to production...")
    
    endpoint = bot.deploy()
    
    print(f"✅ Bot deployed successfully!")
    print(f"Webhook URL: {endpoint}/chat")
    print(f"Health check: {endpoint}/health")
    
    print("\n📝 Next steps:")
    print("1. Add the webhook URL to your Slack app settings")
    print("2. Configure your chat platform to send messages to the endpoint")
    print("3. Test with real users!")
    
    return endpoint

if __name__ == "__main__":
    # Run local tests first
    test_bot()
    
    # Deploy if tests pass
    deploy_choice = input("\nDeploy to production? (y/N): ")
    if deploy_choice.lower() == 'y':
        deploy_bot()
```

## Integration Examples

### Slack Integration

Once deployed, integrate with Slack:

```python title="slack_webhook.py"
# This would be your Slack app's webhook handler
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FLOWSTACK_ENDPOINT = "https://api.flowstack.fun/agents/company-assistant/chat"
FLOWSTACK_API_KEY = "fs_your_api_key_here"

@app.route('/slack/events', methods=['POST'])
def handle_slack_event():
    data = request.json
    
    # Handle Slack challenge for webhook verification
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    # Process message events
    if 'event' in data and data['event']['type'] == 'message':
        event = data['event']
        
        # Skip bot messages to avoid loops
        if 'bot_id' in event:
            return jsonify({'status': 'ignored'})
        
        user_id = event['user']
        text = event['text']
        channel = event['channel']
        
        # Send to FlowStack bot
        response = requests.post(FLOWSTACK_ENDPOINT, 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': FLOWSTACK_API_KEY
            },
            json={
                'message': f"{text} (user_id: {user_id})",
                'context': {
                    'platform': 'slack',
                    'channel': channel,
                    'user': user_id
                }
            }
        )
        
        if response.status_code == 200:
            bot_reply = response.json()['message']
            
            # Send reply back to Slack
            # (You'd use Slack's Web API here)
            send_slack_message(channel, bot_reply)
    
    return jsonify({'status': 'ok'})

def send_slack_message(channel, text):
    """Send message back to Slack channel"""
    # Implementation depends on your Slack app setup
    pass

if __name__ == '__main__':
    app.run(port=3000)
```

### Discord Integration

```python title="discord_bot.py"
import discord
import requests
import asyncio

FLOWSTACK_ENDPOINT = "https://api.flowstack.fun/agents/company-assistant/chat"
FLOWSTACK_API_KEY = "fs_your_api_key_here"

class FlowStackBot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
    
    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return
        
        # Only respond to direct messages or mentions
        if not (isinstance(message.channel, discord.DMChannel) or 
                self.user.mentioned_in(message)):
            return
        
        # Clean the message
        content = message.content.replace(f'<@{self.user.id}>', '').strip()
        
        # Send to FlowStack
        try:
            response = requests.post(FLOWSTACK_ENDPOINT,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': FLOWSTACK_API_KEY
                },
                json={
                    'message': f"{content} (user_id: {message.author.id})",
                    'context': {
                        'platform': 'discord',
                        'guild': str(message.guild.id) if message.guild else None,
                        'channel': str(message.channel.id),
                        'user': str(message.author.id)
                    }
                }
            )
            
            if response.status_code == 200:
                bot_reply = response.json()['message']
                await message.reply(bot_reply)
            else:
                await message.reply("Sorry, I'm having trouble right now. Please try again later.")
                
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("Oops! Something went wrong.")

# Run the Discord bot
client = FlowStackBot()
client.run('YOUR_DISCORD_BOT_TOKEN')
```

## Advanced Features

### Analytics Dashboard

Add usage tracking to understand how your bot is being used:

```python
@bot.tool
def track_bot_usage(user_id: str, action: str, details: dict = None) -> dict:
    """Track bot usage for analytics"""
    
    usage_event = {
        'user_id': user_id,
        'action': action,
        'details': details or {},
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat(),
        'hour': datetime.now().hour
    }
    
    bot.vault.store('usage_analytics', usage_event)
    
    return {'tracked': True, 'action': action}

@bot.tool
def get_bot_analytics(days: int = 7) -> dict:
    """Get bot usage analytics"""
    
    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
    
    events = bot.vault.query('usage_analytics', {
        'date': {'$gte': cutoff_date}
    })
    
    # Analyze usage patterns
    total_events = len(events)
    unique_users = len(set(event['user_id'] for event in events))
    
    # Most common actions
    action_counts = {}
    for event in events:
        action = event['action']
        action_counts[action] = action_counts.get(action, 0) + 1
    
    # Peak usage hours
    hour_counts = {}
    for event in events:
        hour = event['hour']
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    return {
        'period_days': days,
        'total_interactions': total_events,
        'unique_users': unique_users,
        'top_actions': sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        'peak_hours': sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    }
```

### Smart Suggestions

Make your bot proactive by suggesting actions:

```python
@bot.tool
def suggest_next_actions(user_id: str) -> dict:
    """Suggest relevant actions based on user history"""
    
    # Get user's recent activity
    recent_conversations = bot.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=5)
    
    # Get user preferences
    prefs = bot.vault.retrieve('user_preferences', key=user_id)
    
    suggestions = []
    
    # Check if they haven't checked vacation days recently
    vacation_checks = [conv for conv in recent_conversations 
                      if 'vacation' in conv.get('summary', '').lower()]
    
    if not vacation_checks:
        suggestions.append({
            'action': 'check_vacation_days',
            'text': "Check your remaining vacation days",
            'reason': "You haven't checked lately"
        })
    
    # Suggest based on preferences
    if prefs and 'communication_style' not in prefs.get('preferences', {}):
        suggestions.append({
            'action': 'set_communication_preference',
            'text': "Set your communication preferences",
            'reason': "This helps me tailor responses to your style"
        })
    
    return {
        'user_id': user_id,
        'suggestions': suggestions,
        'suggestion_count': len(suggestions)
    }
```

## Deployment Checklist

Before going live with your chatbot:

- [ ] **Test all tools** with various inputs
- [ ] **Set up error handling** for external API failures
- [ ] **Configure rate limiting** in your chat platform
- [ ] **Add logging** for debugging production issues
- [ ] **Set up monitoring** for usage patterns
- [ ] **Create user onboarding** flow
- [ ] **Document bot capabilities** for users
- [ ] **Plan for scaling** as user base grows

## Next Steps

<div class="grid cards" markdown>

-   :material-robot-excited:{ .lg .middle } **[Automation Agent](automation-agent.md)**

    ---

    Build workflow automation that's more powerful than Zapier

-   :material-memory:{ .lg .middle } **[Stateful Agent](stateful-agent.md)**

    ---

    Create agents that learn and remember across sessions

-   :material-swap-horizontal:{ .lg .middle } **[Multi-Provider Setup](multi-provider.md)**

    ---

    Switch between AI providers to optimize costs and capabilities

</div>

---

!!! success "You Built a Production Chatbot!"
    In under an hour, you've created a chatbot that can handle real users, remember conversations, and integrate with existing systems. The bot automatically scales from 1 to 1000s of users without any infrastructure work from you.

Your chatbot now has:
✅ **Memory** - Remembers users and conversations  
✅ **Tools** - Can perform real actions  
✅ **Integration** - Works with Slack, Discord, etc.  
✅ **Analytics** - Tracks usage patterns  
✅ **Scaling** - Handles growth automatically  