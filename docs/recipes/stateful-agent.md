# Recipe: Stateful Agent with Memory

Build an AI agent that learns and remembers across sessions, creating personalized experiences that improve over time.

!!! tip "Perfect for Personalized Applications"
    This recipe shows how to build agents that remember user preferences, learn from interactions, and provide increasingly personalized responses.

## What You'll Build

A stateful agent that can:

- 🧠 **Remember user preferences** and conversation history
- 📚 **Learn from interactions** and improve responses over time
- 👤 **Personalize experiences** based on user behavior patterns
- 🔄 **Maintain context** across multiple sessions
- 📊 **Track user journey** and engagement patterns
- 🎯 **Adapt behavior** based on user feedback

## The Complete Code

```python title="learning_agent.py"
from flowstack import Agent
from datetime import datetime, timedelta
import json
import statistics

# Initialize the learning agent
agent = Agent(
    name="personal-learning-assistant",
    api_key="fs_your_api_key_here",
    system_prompt="""You are a personal learning assistant that remembers everything about your users. You should:
    - Remember user preferences, goals, and past conversations
    - Learn from user feedback and adapt your responses
    - Provide increasingly personalized and relevant help
    - Track user progress and celebrate achievements
    - Suggest next steps based on user patterns and history
    
    Always check user history and preferences before responding to provide the most relevant help."""
)

# Tool 1: User Profile Management
@agent.tool
def get_user_profile(user_id: str) -> dict:
    """Get comprehensive user profile including preferences and history"""
    
    # Get base profile
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'preferences': {},
        'goals': [],
        'learning_style': 'unknown',
        'interaction_count': 0,
        'last_interaction': None
    }
    
    # Get conversation history stats
    conversations = agent.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=10)
    
    # Get learning progress
    progress = agent.vault.query('learning_progress', {
        'user_id': user_id
    })
    
    # Get user feedback history
    feedback = agent.vault.query('user_feedback', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=5)
    
    return {
        'profile': profile,
        'recent_conversations': len(conversations),
        'total_learning_items': len(progress),
        'recent_feedback': feedback,
        'engagement_score': calculate_engagement_score(profile, conversations, feedback)
    }

def calculate_engagement_score(profile: dict, conversations: list, feedback: list) -> float:
    """Calculate user engagement score based on various factors"""
    score = 0.0
    
    # Base score from interaction frequency
    interaction_count = profile.get('interaction_count', 0)
    if interaction_count > 0:
        score += min(interaction_count * 2, 50)  # Up to 50 points for interactions
    
    # Recent activity bonus
    if conversations:
        latest_conversation = conversations[0]
        days_since_last = (datetime.now() - datetime.fromisoformat(latest_conversation['timestamp'])).days
        if days_since_last < 7:
            score += 20  # Recent activity bonus
    
    # Feedback quality bonus
    positive_feedback = [f for f in feedback if f.get('rating', 0) >= 4]
    if feedback:
        feedback_ratio = len(positive_feedback) / len(feedback)
        score += feedback_ratio * 30  # Up to 30 points for good feedback
    
    return min(score, 100)  # Cap at 100

@agent.tool
def update_user_preferences(user_id: str, preference_type: str, value: str, context: str = "") -> dict:
    """Update user preferences with learning context"""
    
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'preferences': {},
        'goals': [],
        'learning_style': 'unknown',
        'interaction_count': 0
    }
    
    # Update preference
    old_value = profile['preferences'].get(preference_type)
    profile['preferences'][preference_type] = value
    profile['updated_at'] = datetime.now().isoformat()
    
    # Log the preference change for learning
    preference_change = {
        'user_id': user_id,
        'preference_type': preference_type,
        'old_value': old_value,
        'new_value': value,
        'context': context,
        'timestamp': datetime.now().isoformat()
    }
    
    agent.vault.store('preference_changes', preference_change)
    agent.vault.store('user_profiles', profile, key=user_id)
    
    return {
        'message': f"Updated {preference_type} preference to: {value}",
        'previous_value': old_value,
        'context': context,
        'learning_opportunity': old_value != value  # Did we learn something new?
    }

# Tool 2: Conversation Memory and Context
@agent.tool
def save_conversation_context(user_id: str, conversation_summary: str, key_points: list, user_mood: str = "neutral") -> dict:
    """Save conversation context for future reference"""
    
    conversation = {
        'user_id': user_id,
        'summary': conversation_summary,
        'key_points': key_points,
        'user_mood': user_mood,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat(),
        'interaction_type': 'conversation'
    }
    
    conv_key = agent.vault.store('conversations', conversation)
    
    # Update user profile interaction count
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    profile['interaction_count'] = profile.get('interaction_count', 0) + 1
    profile['last_interaction'] = datetime.now().isoformat()
    agent.vault.store('user_profiles', profile, key=user_id)
    
    # Analyze conversation for learning insights
    insights = analyze_conversation_for_insights(user_id, conversation)
    
    return {
        'conversation_id': conv_key,
        'summary': conversation_summary,
        'insights_learned': len(insights),
        'insights': insights
    }

def analyze_conversation_for_insights(user_id: str, conversation: dict) -> list:
    """Analyze conversation to extract learning insights"""
    insights = []
    
    # Mood pattern analysis
    mood = conversation.get('user_mood', 'neutral')
    if mood in ['frustrated', 'confused']:
        insights.append({
            'type': 'mood_pattern',
            'insight': f"User expressed {mood} - may need simpler explanations or different approach",
            'action': 'adjust_communication_style'
        })
    elif mood in ['excited', 'satisfied']:
        insights.append({
            'type': 'positive_pattern',
            'insight': f"User was {mood} - current approach is working well",
            'action': 'continue_current_style'
        })
    
    # Key points analysis
    key_points = conversation.get('key_points', [])
    if 'deadline' in ' '.join(key_points).lower():
        insights.append({
            'type': 'urgency_pattern',
            'insight': "User mentioned deadline - prioritize time-sensitive responses",
            'action': 'flag_urgent_followups'
        })
    
    if any(point.lower().startswith('learn') for point in key_points):
        insights.append({
            'type': 'learning_intent',
            'insight': "User expressed learning intent - provide educational resources",
            'action': 'suggest_learning_materials'
        })
    
    return insights

@agent.tool
def recall_relevant_context(user_id: str, current_topic: str, limit: int = 5) -> dict:
    """Recall relevant conversation history and context for current topic"""
    
    # Get recent conversations
    recent_conversations = agent.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=20)
    
    # Filter for topic relevance (simple keyword matching - could be enhanced with embeddings)
    relevant_conversations = []
    topic_keywords = current_topic.lower().split()
    
    for conv in recent_conversations:
        conv_text = f"{conv.get('summary', '')} {' '.join(conv.get('key_points', []))}".lower()
        if any(keyword in conv_text for keyword in topic_keywords):
            relevant_conversations.append(conv)
    
    # Get user preferences related to current topic
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    relevant_preferences = {}
    for pref_key, pref_value in profile.get('preferences', {}).items():
        if any(keyword in pref_key.lower() for keyword in topic_keywords):
            relevant_preferences[pref_key] = pref_value
    
    # Get learning progress on this topic
    learning_progress = agent.vault.query('learning_progress', {
        'user_id': user_id,
        'topic': {'$regex': current_topic, '$options': 'i'}
    })
    
    return {
        'current_topic': current_topic,
        'relevant_conversations': relevant_conversations[:limit],
        'relevant_preferences': relevant_preferences,
        'learning_progress': learning_progress,
        'context_items_found': len(relevant_conversations) + len(relevant_preferences) + len(learning_progress)
    }

# Tool 3: Learning Progress Tracking
@agent.tool
def track_learning_progress(user_id: str, topic: str, skill_level: str, progress_notes: str) -> dict:
    """Track user's learning progress on specific topics"""
    
    # Check for existing progress on this topic
    existing_progress = agent.vault.query('learning_progress', {
        'user_id': user_id,
        'topic': topic
    })
    
    if existing_progress:
        # Update existing progress
        progress_record = existing_progress[0]
        old_level = progress_record.get('skill_level', 'beginner')
        progress_record.update({
            'skill_level': skill_level,
            'progress_notes': progress_notes,
            'updated_at': datetime.now().isoformat(),
            'sessions_count': progress_record.get('sessions_count', 0) + 1
        })
        
        # Add to progress history
        if 'history' not in progress_record:
            progress_record['history'] = []
        progress_record['history'].append({
            'previous_level': old_level,
            'new_level': skill_level,
            'notes': progress_notes,
            'timestamp': datetime.now().isoformat()
        })
        
        agent.vault.store('learning_progress', progress_record, key=progress_record.get('_id'))
        
        return {
            'topic': topic,
            'progress_type': 'updated',
            'old_level': old_level,
            'new_level': skill_level,
            'sessions_count': progress_record['sessions_count'],
            'improvement_detected': skill_level != old_level
        }
    else:
        # Create new progress record
        progress_record = {
            'user_id': user_id,
            'topic': topic,
            'skill_level': skill_level,
            'progress_notes': progress_notes,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'sessions_count': 1,
            'history': []
        }
        
        progress_key = agent.vault.store('learning_progress', progress_record)
        
        return {
            'topic': topic,
            'progress_type': 'new',
            'skill_level': skill_level,
            'progress_id': progress_key,
            'message': f'Started tracking progress on {topic} at {skill_level} level'
        }

# Tool 4: Feedback Learning System
@agent.tool
def collect_user_feedback(user_id: str, interaction_id: str, rating: int, feedback_text: str, suggestion: str = "") -> dict:
    """Collect and learn from user feedback"""
    
    feedback_record = {
        'user_id': user_id,
        'interaction_id': interaction_id,
        'rating': rating,  # 1-5 scale
        'feedback_text': feedback_text,
        'suggestion': suggestion,
        'timestamp': datetime.now().isoformat(),
        'processed': False
    }
    
    feedback_key = agent.vault.store('user_feedback', feedback_record)
    
    # Process feedback for learning insights
    learning_insights = process_feedback_for_learning(user_id, feedback_record)
    
    # Update user profile based on feedback
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    
    # Track satisfaction trends
    if 'satisfaction_history' not in profile:
        profile['satisfaction_history'] = []
    
    profile['satisfaction_history'].append({
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 20 ratings
    profile['satisfaction_history'] = profile['satisfaction_history'][-20:]
    
    # Calculate average satisfaction
    recent_ratings = [r['rating'] for r in profile['satisfaction_history'][-10:]]
    profile['avg_satisfaction'] = statistics.mean(recent_ratings) if recent_ratings else rating
    
    agent.vault.store('user_profiles', profile, key=user_id)
    
    return {
        'feedback_id': feedback_key,
        'rating': rating,
        'learning_insights': learning_insights,
        'avg_satisfaction': profile['avg_satisfaction'],
        'satisfaction_trend': analyze_satisfaction_trend(profile['satisfaction_history'])
    }

def process_feedback_for_learning(user_id: str, feedback: dict) -> list:
    """Process feedback to extract learning insights"""
    insights = []
    
    rating = feedback.get('rating', 3)
    feedback_text = feedback.get('feedback_text', '').lower()
    
    # Low rating analysis
    if rating <= 2:
        if 'too complex' in feedback_text or 'confusing' in feedback_text:
            insights.append({
                'type': 'communication_adjustment',
                'insight': 'User finds responses too complex - simplify language',
                'adjustment': 'use_simpler_language'
            })
        
        if 'slow' in feedback_text or 'long' in feedback_text:
            insights.append({
                'type': 'response_speed',
                'insight': 'User wants faster/shorter responses',
                'adjustment': 'provide_concise_responses'
            })
        
        if 'not relevant' in feedback_text or 'not helpful' in feedback_text:
            insights.append({
                'type': 'relevance_issue',
                'insight': 'Response not relevant to user needs',
                'adjustment': 'improve_context_understanding'
            })
    
    # High rating analysis
    elif rating >= 4:
        if 'clear' in feedback_text or 'helpful' in feedback_text:
            insights.append({
                'type': 'positive_pattern',
                'insight': 'Current communication style works well',
                'adjustment': 'continue_current_approach'
            })
        
        if 'detailed' in feedback_text or 'thorough' in feedback_text:
            insights.append({
                'type': 'detail_preference',
                'insight': 'User appreciates detailed responses',
                'adjustment': 'provide_comprehensive_answers'
            })
    
    return insights

def analyze_satisfaction_trend(satisfaction_history: list) -> str:
    """Analyze satisfaction trend over time"""
    if len(satisfaction_history) < 3:
        return 'insufficient_data'
    
    recent_ratings = [r['rating'] for r in satisfaction_history[-5:]]
    older_ratings = [r['rating'] for r in satisfaction_history[-10:-5]] if len(satisfaction_history) >= 10 else []
    
    if not older_ratings:
        return 'stable'
    
    recent_avg = statistics.mean(recent_ratings)
    older_avg = statistics.mean(older_ratings)
    
    if recent_avg > older_avg + 0.5:
        return 'improving'
    elif recent_avg < older_avg - 0.5:
        return 'declining'
    else:
        return 'stable'

# Tool 5: Personalized Recommendations
@agent.tool
def generate_personalized_recommendations(user_id: str, context: str = "") -> dict:
    """Generate personalized recommendations based on user history and preferences"""
    
    # Get user profile
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    
    # Get learning progress
    learning_progress = agent.vault.query('learning_progress', {
        'user_id': user_id
    })
    
    # Get recent conversations
    recent_conversations = agent.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=10)
    
    # Get feedback patterns
    feedback_history = agent.vault.query('user_feedback', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=10)
    
    recommendations = []
    
    # Learning path recommendations
    if learning_progress:
        topics_in_progress = [p['topic'] for p in learning_progress if p.get('skill_level') not in ['expert', 'advanced']]
        for topic in topics_in_progress:
            recommendations.append({
                'type': 'learning_continuation',
                'title': f'Continue learning {topic}',
                'reason': 'You have ongoing progress in this topic',
                'priority': 'high',
                'topic': topic
            })
    
    # Based on conversation patterns
    conversation_topics = []
    for conv in recent_conversations:
        conversation_topics.extend(conv.get('key_points', []))
    
    # Find frequent topics
    topic_frequency = {}
    for topic in conversation_topics:
        topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
    
    frequent_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for topic, frequency in frequent_topics:
        if frequency >= 2:  # Topic mentioned in multiple conversations
            recommendations.append({
                'type': 'interest_based',
                'title': f'Explore more about {topic}',
                'reason': f'You\'ve discussed {topic} in {frequency} recent conversations',
                'priority': 'medium',
                'topic': topic
            })
    
    # Based on satisfaction trends
    satisfaction_trend = 'stable'
    if profile.get('satisfaction_history'):
        satisfaction_trend = analyze_satisfaction_trend(profile['satisfaction_history'])
    
    if satisfaction_trend == 'declining':
        recommendations.append({
            'type': 'experience_improvement',
            'title': 'Let\'s improve your experience',
            'reason': 'Your satisfaction has been declining - let\'s adjust my approach',
            'priority': 'high',
            'action': 'gather_preference_feedback'
        })
    
    # Time-based recommendations
    if profile.get('last_interaction'):
        days_since_last = (datetime.now() - datetime.fromisoformat(profile['last_interaction'])).days
        if days_since_last >= 7:
            recommendations.append({
                'type': 'engagement',
                'title': 'Welcome back! Let\'s catch up',
                'reason': f'It\'s been {days_since_last} days since our last conversation',
                'priority': 'medium',
                'action': 'status_check'
            })
    
    return {
        'user_id': user_id,
        'recommendations': recommendations,
        'recommendation_count': len(recommendations),
        'personalization_factors': {
            'learning_topics': len(learning_progress),
            'conversation_history': len(recent_conversations),
            'satisfaction_trend': satisfaction_trend,
            'engagement_score': calculate_engagement_score(profile, recent_conversations, feedback_history)
        }
    }

# Tool 6: Adaptive Response Style
@agent.tool
def adapt_response_style(user_id: str, message_content: str) -> dict:
    """Adapt response style based on user history and preferences"""
    
    # Get user preferences
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    preferences = profile.get('preferences', {})
    
    # Get recent feedback to understand communication preferences
    recent_feedback = agent.vault.query('user_feedback', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=5)
    
    # Analyze feedback for communication adjustments
    style_adjustments = []
    for feedback in recent_feedback:
        rating = feedback.get('rating', 3)
        feedback_text = feedback.get('feedback_text', '').lower()
        
        if rating <= 2:
            if 'too long' in feedback_text:
                style_adjustments.append('be_more_concise')
            if 'too technical' in feedback_text:
                style_adjustments.append('use_simpler_language')
            if 'too formal' in feedback_text:
                style_adjustments.append('be_more_casual')
        elif rating >= 4:
            if 'detailed' in feedback_text:
                style_adjustments.append('provide_comprehensive_answers')
            if 'professional' in feedback_text:
                style_adjustments.append('maintain_formal_tone')
    
    # Determine response style
    response_style = {
        'tone': preferences.get('communication_tone', 'friendly'),
        'detail_level': preferences.get('detail_preference', 'medium'),
        'formality': preferences.get('formality_preference', 'professional'),
        'adjustments': list(set(style_adjustments))  # Remove duplicates
    }
    
    # Apply recent learning from feedback
    if 'be_more_concise' in style_adjustments:
        response_style['detail_level'] = 'brief'
    if 'use_simpler_language' in style_adjustments:
        response_style['complexity'] = 'simple'
    if 'be_more_casual' in style_adjustments:
        response_style['tone'] = 'casual'
    
    return {
        'user_id': user_id,
        'response_style': response_style,
        'style_source': 'learned_from_feedback' if style_adjustments else 'user_preferences',
        'adaptations_applied': len(style_adjustments)
    }

# Test the learning agent
def test_learning_agent():
    """Test the learning agent with sample interactions"""
    print("🧠 Testing Personal Learning Assistant")
    print("=" * 50)
    
    user_id = "test_user_123"
    
    # Test 1: Initial interaction - should have no history
    print("\n1. First interaction (no history)...")
    response = agent.chat(f"Hello! I'm new here. My user ID is {user_id}")
    print(f"Agent: {response}")
    
    # Test 2: Set some preferences
    print("\n2. Setting user preferences...")
    response = agent.chat(f"I prefer concise responses and technical explanations. My user ID is {user_id}")
    print(f"Agent: {response}")
    
    # Test 3: Track learning progress
    print("\n3. Tracking learning progress...")
    response = agent.chat(f"I'm learning Python programming and I'm at beginner level. My user ID is {user_id}")
    print(f"Agent: {response}")
    
    # Test 4: Provide feedback
    print("\n4. Providing feedback...")
    response = agent.chat(f"That was very helpful! I'd rate our conversation 5/5. My user ID is {user_id}")
    print(f"Agent: {response}")
    
    # Test 5: Return later - should remember everything
    print("\n5. Returning user (should remember context)...")
    response = agent.chat(f"Hi again! How's my Python learning progress? My user ID is {user_id}")
    print(f"Agent: {response}")
    
    print("\n✅ Learning agent testing complete!")

# Deploy the learning agent
def deploy_learning_agent():
    """Deploy the learning agent to production"""
    print("\n🚀 Deploying learning agent...")
    
    endpoint = agent.deploy()
    
    print(f"✅ Learning agent deployed!")
    print(f"Chat endpoint: {endpoint}/chat")
    
    print("\n🧠 Your agent now has:")
    print("• Memory of all user interactions")
    print("• Learning from user feedback")
    print("• Personalized recommendations")
    print("• Adaptive response styles")
    print("• Progress tracking capabilities")
    
    return endpoint

if __name__ == "__main__":
    # Run tests
    test_learning_agent()
    
    # Deploy
    deploy_choice = input("\nDeploy learning agent? (y/N): ")
    if deploy_choice.lower() == 'y':
        deploy_learning_agent()
```

## Advanced Learning Patterns

### User Journey Mapping

```python
@agent.tool
def map_user_journey(user_id: str) -> dict:
    """Map the user's journey and identify patterns"""
    
    # Get all user interactions
    conversations = agent.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', 1)])  # Chronological order
    
    learning_progress = agent.vault.query('learning_progress', {
        'user_id': user_id
    }, sort=[('created_at', 1)])
    
    feedback = agent.vault.query('user_feedback', {
        'user_id': user_id
    }, sort=[('timestamp', 1)])
    
    # Analyze journey phases
    journey_phases = []
    
    if conversations:
        # Onboarding phase (first 3 interactions)
        onboarding_convs = conversations[:3]
        onboarding_phase = {
            'phase': 'onboarding',
            'duration_days': calculate_phase_duration(onboarding_convs),
            'interaction_count': len(onboarding_convs),
            'key_topics': extract_topics_from_conversations(onboarding_convs)
        }
        journey_phases.append(onboarding_phase)
        
        # Growth phase (active learning period)
        if len(conversations) > 3:
            growth_convs = conversations[3:]
            growth_phase = {
                'phase': 'growth',
                'duration_days': calculate_phase_duration(growth_convs),
                'interaction_count': len(growth_convs),
                'learning_topics': len(learning_progress),
                'avg_satisfaction': calculate_avg_satisfaction_for_period(feedback)
            }
            journey_phases.append(growth_phase)
    
    # Identify engagement patterns
    engagement_patterns = analyze_engagement_patterns(conversations)
    
    return {
        'user_id': user_id,
        'journey_phases': journey_phases,
        'engagement_patterns': engagement_patterns,
        'total_interactions': len(conversations),
        'learning_topics_explored': len(learning_progress),
        'journey_insights': generate_journey_insights(journey_phases, engagement_patterns)
    }

def calculate_phase_duration(conversations: list) -> int:
    """Calculate duration of a phase in days"""
    if len(conversations) < 2:
        return 0
    
    start_date = datetime.fromisoformat(conversations[0]['timestamp'])
    end_date = datetime.fromisoformat(conversations[-1]['timestamp'])
    return (end_date - start_date).days

def extract_topics_from_conversations(conversations: list) -> list:
    """Extract key topics from conversations"""
    all_topics = []
    for conv in conversations:
        all_topics.extend(conv.get('key_points', []))
    
    # Count frequency and return top topics
    topic_freq = {}
    for topic in all_topics:
        topic_freq[topic] = topic_freq.get(topic, 0) + 1
    
    return sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:5]

def analyze_engagement_patterns(conversations: list) -> dict:
    """Analyze user engagement patterns"""
    if not conversations:
        return {}
    
    # Calculate time between interactions
    intervals = []
    for i in range(1, len(conversations)):
        prev_time = datetime.fromisoformat(conversations[i-1]['timestamp'])
        curr_time = datetime.fromisoformat(conversations[i]['timestamp'])
        intervals.append((curr_time - prev_time).days)
    
    # Identify patterns
    patterns = {
        'avg_days_between_interactions': statistics.mean(intervals) if intervals else 0,
        'most_active_period': find_most_active_period(conversations),
        'consistency_score': calculate_consistency_score(intervals)
    }
    
    return patterns

def find_most_active_period(conversations: list) -> str:
    """Find the most active period for the user"""
    if not conversations:
        return 'no_data'
    
    # Group by week
    weekly_counts = {}
    for conv in conversations:
        date = datetime.fromisoformat(conv['timestamp']).date()
        week_start = date - timedelta(days=date.weekday())
        weekly_counts[week_start] = weekly_counts.get(week_start, 0) + 1
    
    if not weekly_counts:
        return 'no_data'
    
    most_active_week = max(weekly_counts.items(), key=lambda x: x[1])
    return f"Week of {most_active_week[0]} ({most_active_week[1]} interactions)"
```

### Predictive Insights

```python
@agent.tool
def predict_user_needs(user_id: str) -> dict:
    """Predict what the user might need based on patterns"""
    
    # Get user data
    profile = agent.vault.retrieve('user_profiles', key=user_id) or {}
    conversations = agent.vault.query('conversations', {
        'user_id': user_id
    }, sort=[('timestamp', -1)], limit=20)
    
    learning_progress = agent.vault.query('learning_progress', {
        'user_id': user_id
    })
    
    predictions = []
    
    # Predict based on learning progress
    for progress in learning_progress:
        topic = progress['topic']
        skill_level = progress['skill_level']
        last_update = datetime.fromisoformat(progress['updated_at'])
        days_since_update = (datetime.now() - last_update).days
        
        if skill_level == 'beginner' and days_since_update > 7:
            predictions.append({
                'type': 'learning_support',
                'prediction': f'User may need encouragement to continue learning {topic}',
                'confidence': 0.8,
                'suggested_action': 'offer_practice_exercises'
            })
        elif skill_level == 'intermediate' and days_since_update > 14:
            predictions.append({
                'type': 'advancement_opportunity',
                'prediction': f'User ready for advanced {topic} concepts',
                'confidence': 0.7,
                'suggested_action': 'suggest_advanced_topics'
            })
    
    # Predict based on conversation patterns
    if conversations:
        recent_moods = [c.get('user_mood', 'neutral') for c in conversations[:5]]
        frustrated_count = recent_moods.count('frustrated')
        
        if frustrated_count >= 2:
            predictions.append({
                'type': 'support_needed',
                'prediction': 'User showing signs of frustration - may need different approach',
                'confidence': 0.9,
                'suggested_action': 'adjust_teaching_style'
            })
        
        # Check for declining engagement
        interaction_gaps = []
        for i in range(1, min(5, len(conversations))):
            gap = (datetime.fromisoformat(conversations[i-1]['timestamp']) - 
                  datetime.fromisoformat(conversations[i]['timestamp'])).days
            interaction_gaps.append(gap)
        
        if interaction_gaps and statistics.mean(interaction_gaps) > 7:
            predictions.append({
                'type': 'engagement_risk',
                'prediction': 'User engagement declining - may need re-engagement',
                'confidence': 0.7,
                'suggested_action': 'send_check_in_message'
            })
    
    return {
        'user_id': user_id,
        'predictions': predictions,
        'prediction_count': len(predictions),
        'generated_at': datetime.now().isoformat()
    }
```

## Integration Examples

### Progressive Web App Integration

```javascript title="learning_app.js"
class LearningAssistant {
    constructor(apiKey, endpoint) {
        this.apiKey = apiKey;
        this.endpoint = endpoint;
        this.userId = this.getUserId();
    }
    
    async sendMessage(message) {
        const response = await fetch(`${this.endpoint}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({
                message: `${message} (user_id: ${this.userId})`,
                context: {
                    platform: 'web_app',
                    session_id: this.getSessionId()
                }
            })
        });
        
        return await response.json();
    }
    
    async trackLearningProgress(topic, level, notes) {
        return await this.sendMessage(
            `Track my learning progress: Topic: ${topic}, Level: ${level}, Notes: ${notes}`
        );
    }
    
    async provideFeedback(interactionId, rating, feedback) {
        return await this.sendMessage(
            `Feedback for interaction ${interactionId}: Rating: ${rating}/5, Feedback: ${feedback}`
        );
    }
    
    async getPersonalizedRecommendations() {
        return await this.sendMessage(
            'What would you recommend for me to learn or explore next?'
        );
    }
    
    getUserId() {
        // Get or generate user ID
        let userId = localStorage.getItem('learning_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('learning_user_id', userId);
        }
        return userId;
    }
    
    getSessionId() {
        // Generate session ID for this browser session
        if (!this.sessionId) {
            this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        return this.sessionId;
    }
}

// Usage example
const assistant = new LearningAssistant('fs_your_api_key', 'https://api.flowstack.fun/agents/personal-learning-assistant');

// Track a learning session
assistant.trackLearningProgress('JavaScript', 'intermediate', 'Completed async/await tutorial');

// Get personalized recommendations
assistant.getPersonalizedRecommendations().then(response => {
    console.log('Recommendations:', response);
});
```

## Next Steps

<div class="grid cards" markdown>

-   :material-swap-horizontal:{ .lg .middle } **[Multi-Provider Setup](multi-provider.md)**

    ---

    Optimize costs and capabilities across different AI providers

-   :material-robot-excited:{ .lg .middle } **[Chatbot Agent](chatbot.md)**

    ---

    Build conversational interfaces with memory and learning

-   :material-cog-transfer:{ .lg .middle } **[Automation Agent](automation-agent.md)**

    ---

    Create intelligent workflows that remember and adapt

</div>

---

!!! success "You Built a Learning Agent!"
    You've created an AI agent that truly learns and adapts to each user. Unlike traditional chatbots that forget everything after each conversation, your agent builds deeper relationships and provides increasingly personalized experiences.

Your learning agent now has:
✅ **Persistent Memory** - Remembers everything about each user  
✅ **Feedback Learning** - Improves responses based on user ratings  
✅ **Progress Tracking** - Monitors user learning and growth  
✅ **Predictive Insights** - Anticipates user needs  
✅ **Adaptive Communication** - Adjusts style based on preferences  
✅ **Journey Mapping** - Understands user patterns over time  