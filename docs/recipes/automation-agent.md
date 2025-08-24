# Recipe: Automation Agent (Zapier Killer)

Build intelligent workflow automation that remembers state, makes decisions, and handles complex multi-step processes.

!!! tip "Perfect for Automation Enthusiasts"
    This recipe shows how to build stateful automation that's more powerful than Zapier or n8n, with AI decision-making and persistent memory.

## What You'll Build

An automation agent that can:

- 🔄 **Handle multi-step workflows** with conditional logic
- 🧠 **Make intelligent decisions** based on data and context
- 💾 **Remember state** between workflow runs
- 📊 **Track and analyze** workflow performance
- 🔗 **Integrate with any API** or service
- ⚡ **Trigger on schedules** or external events

## The Complete Code

```python title="automation_agent.py"
from flowstack import Agent, tool, DataVault
from datetime import datetime, timedelta
import json
import hashlib

# Initialize the automation agent
automation = Agent(
    name="workflow-automation",
    api_key="fs_your_api_key_here",
    instructions="""You are an intelligent workflow automation agent. You can:
    - Execute multi-step workflows with decision points
    - Remember workflow state and history
    - Make smart decisions based on data and context
    - Handle errors gracefully and retry operations
    - Learn from past workflow executions to improve performance
    
    Always think through workflows step by step and use the available tools effectively."""
)

# Initialize DataVault for persistent storage
vault = DataVault(api_key="fs_your_api_key_here")

# Tool 1: Lead Scoring and CRM Automation
@tool
def process_new_lead(lead_data: dict) -> dict:
    """Process a new lead through the qualification workflow"""
    
    lead_id = lead_data.get('id') or f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Calculate lead score
    score = calculate_lead_score(lead_data)
    
    # Determine workflow path based on score
    workflow_steps = []
    
    if score >= 80:
        # High-value lead: immediate personal outreach
        workflow_steps = [
            'send_immediate_alert_to_sales',
            'create_high_priority_crm_record', 
            'schedule_personal_followup',
            'add_to_hot_leads_sequence'
        ]
        priority = 'high'
    elif score >= 50:
        # Medium lead: nurture sequence
        workflow_steps = [
            'create_crm_record',
            'add_to_nurture_sequence',
            'schedule_followup_in_3_days',
            'send_educational_content'
        ]
        priority = 'medium'
    else:
        # Low score: basic tracking
        workflow_steps = [
            'create_basic_crm_record',
            'add_to_newsletter',
            'schedule_followup_in_2_weeks'
        ]
        priority = 'low'
    
    # Create workflow instance
    workflow = {
        'id': f"workflow_{lead_id}",
        'lead_id': lead_id,
        'lead_data': lead_data,
        'score': score,
        'priority': priority,
        'steps': workflow_steps,
        'current_step': 0,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat(),
        'results': []
    }
    
    # Store workflow state
    vault.store('workflows', workflow, key=workflow['id'])
    
    # Execute first step
    result = execute_workflow_step(workflow['id'])
    
    return {
        'lead_id': lead_id,
        'workflow_id': workflow['id'],
        'score': score,
        'priority': priority,
        'first_step_result': result
    }

def calculate_lead_score(lead_data: dict) -> int:
    """Calculate lead score based on various factors"""
    score = 0
    
    # Company size scoring
    company_size = lead_data.get('company_size', 0)
    if company_size > 1000:
        score += 30
    elif company_size > 100:
        score += 20
    elif company_size > 10:
        score += 10
    
    # Industry scoring
    high_value_industries = ['technology', 'finance', 'healthcare', 'manufacturing']
    if lead_data.get('industry', '').lower() in high_value_industries:
        score += 25
    
    # Role scoring
    decision_maker_roles = ['ceo', 'cto', 'vp', 'director', 'head of', 'chief']
    role = lead_data.get('role', '').lower()
    if any(title in role for title in decision_maker_roles):
        score += 30
    elif 'manager' in role:
        score += 15
    
    # Engagement scoring
    if lead_data.get('downloaded_whitepaper'):
        score += 15
    if lead_data.get('attended_webinar'):
        score += 20
    if lead_data.get('requested_demo'):
        score += 35
    
    # Budget indication
    if lead_data.get('budget_indicated', 0) > 50000:
        score += 25
    elif lead_data.get('budget_indicated', 0) > 10000:
        score += 15
    
    return min(score, 100)  # Cap at 100

@tool
def execute_workflow_step(workflow_id: str) -> dict:
    """Execute the next step in a workflow"""
    
    # Get workflow state
    workflow = vault.retrieve('workflows', key=workflow_id)
    if not workflow:
        return {'error': 'Workflow not found'}
    
    if workflow['status'] != 'in_progress':
        return {'message': f'Workflow is {workflow["status"]}', 'workflow_id': workflow_id}
    
    # Check if workflow is complete
    if workflow['current_step'] >= len(workflow['steps']):
        workflow['status'] = 'completed'
        workflow['completed_at'] = datetime.now().isoformat()
        vault.store('workflows', workflow, key=workflow_id)
        return {'message': 'Workflow completed', 'workflow_id': workflow_id}
    
    # Execute current step
    current_step = workflow['steps'][workflow['current_step']]
    step_result = execute_step_action(current_step, workflow)
    
    # Record result
    step_record = {
        'step': current_step,
        'step_number': workflow['current_step'],
        'result': step_result,
        'executed_at': datetime.now().isoformat()
    }
    workflow['results'].append(step_record)
    
    # Move to next step
    workflow['current_step'] += 1
    workflow['updated_at'] = datetime.now().isoformat()
    
    # Update workflow state
    vault.store('workflows', workflow, key=workflow_id)
    
    return {
        'workflow_id': workflow_id,
        'step_executed': current_step,
        'step_result': step_result,
        'next_step': workflow['steps'][workflow['current_step']] if workflow['current_step'] < len(workflow['steps']) else 'completed',
        'progress': f"{workflow['current_step']}/{len(workflow['steps'])}"
    }

def execute_step_action(step: str, workflow: dict) -> dict:
    """Execute a specific workflow step action"""
    
    lead_data = workflow['lead_data']
    
    if step == 'send_immediate_alert_to_sales':
        # In real implementation, this would send Slack/email alert
        return {
            'action': 'sales_alert_sent',
            'message': f"High-value lead alert sent for {lead_data.get('name', 'Unknown')}",
            'success': True
        }
    
    elif step == 'create_high_priority_crm_record':
        # In real implementation, this would call CRM API (Salesforce, HubSpot, etc.)
        crm_record = {
            'lead_id': workflow['lead_id'],
            'name': lead_data.get('name'),
            'company': lead_data.get('company'),
            'email': lead_data.get('email'),
            'priority': 'high',
            'score': workflow['score'],
            'created_at': datetime.now().isoformat()
        }
        vault.store('crm_records', crm_record, key=workflow['lead_id'])
        return {'action': 'crm_record_created', 'priority': 'high', 'success': True}
    
    elif step == 'schedule_personal_followup':
        # Schedule followup task
        followup = {
            'lead_id': workflow['lead_id'],
            'type': 'personal_call',
            'scheduled_for': (datetime.now() + timedelta(hours=2)).isoformat(),
            'assigned_to': 'sales_team',
            'priority': 'high'
        }
        vault.store('followup_tasks', followup, key=f"followup_{workflow['lead_id']}")
        return {'action': 'followup_scheduled', 'scheduled_for': followup['scheduled_for'], 'success': True}
    
    elif step == 'add_to_nurture_sequence':
        # Add to email nurture sequence
        sequence = {
            'lead_id': workflow['lead_id'],
            'sequence_type': 'nurture',
            'current_email': 1,
            'total_emails': 5,
            'started_at': datetime.now().isoformat(),
            'next_email_date': (datetime.now() + timedelta(days=1)).isoformat()
        }
        vault.store('email_sequences', sequence, key=f"seq_{workflow['lead_id']}")
        return {'action': 'added_to_nurture', 'sequence_length': 5, 'success': True}
    
    elif step == 'send_educational_content':
        # Send relevant educational content
        content = {
            'lead_id': workflow['lead_id'],
            'content_type': 'industry_guide',
            'title': f"Best Practices for {lead_data.get('industry', 'Your Industry')}",
            'sent_at': datetime.now().isoformat()
        }
        vault.store('content_delivered', content, key=f"content_{workflow['lead_id']}")
        return {'action': 'content_sent', 'content_type': 'industry_guide', 'success': True}
    
    else:
        # Default action for unhandled steps
        return {'action': step, 'message': f'Step {step} executed', 'success': True}

# Tool 2: E-commerce Order Processing Automation
@tool
def process_order_workflow(order_data: dict) -> dict:
    """Process an e-commerce order through fulfillment workflow"""
    
    order_id = order_data.get('id', f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Determine workflow based on order characteristics
    workflow_steps = ['validate_payment', 'check_inventory', 'reserve_items']
    
    # Add conditional steps based on order
    if order_data.get('total', 0) > 1000:
        workflow_steps.append('fraud_check')
    
    if order_data.get('shipping_country') != 'US':
        workflow_steps.extend(['customs_documentation', 'international_shipping_calculation'])
    
    if any(item.get('custom_engraving') for item in order_data.get('items', [])):
        workflow_steps.append('custom_production_queue')
    
    workflow_steps.extend([
        'generate_shipping_label',
        'send_confirmation_email',
        'update_customer_record'
    ])
    
    # Create workflow
    workflow = {
        'id': f"order_workflow_{order_id}",
        'order_id': order_id,
        'order_data': order_data,
        'steps': workflow_steps,
        'current_step': 0,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat(),
        'results': []
    }
    
    vault.store('order_workflows', workflow, key=workflow['id'])
    
    return {
        'order_id': order_id,
        'workflow_id': workflow['id'],
        'total_steps': len(workflow_steps),
        'message': 'Order workflow started'
    }

# Tool 3: Content Publishing Automation
@tool
def create_content_workflow(content_request: dict) -> dict:
    """Create and execute content publishing workflow"""
    
    content_id = content_request.get('id', f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Determine workflow based on content type
    content_type = content_request.get('type', 'blog_post')
    
    if content_type == 'blog_post':
        workflow_steps = [
            'research_keywords',
            'generate_outline',
            'write_draft',
            'add_images',
            'seo_optimization',
            'schedule_publication',
            'promote_on_social'
        ]
    elif content_type == 'social_media':
        workflow_steps = [
            'generate_post_variations',
            'create_visual_assets',
            'schedule_across_platforms',
            'track_engagement'
        ]
    elif content_type == 'email_newsletter':
        workflow_steps = [
            'gather_content_pieces',
            'create_email_template',
            'segment_audience',
            'schedule_send',
            'track_performance'
        ]
    
    workflow = {
        'id': f"content_workflow_{content_id}",
        'content_id': content_id,
        'content_request': content_request,
        'steps': workflow_steps,
        'current_step': 0,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat(),
        'results': []
    }
    
    vault.store('content_workflows', workflow, key=workflow['id'])
    
    return {
        'content_id': content_id,
        'workflow_id': workflow['id'],
        'content_type': content_type,
        'steps': workflow_steps
    }

# Tool 4: Workflow Analytics and Optimization
@tool
def analyze_workflow_performance(workflow_type: str = None, days: int = 30) -> dict:
    """Analyze workflow performance and identify optimization opportunities"""
    
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Get workflows from the specified period
    query = {'created_at': {'$gte': cutoff_date}}
    if workflow_type:
        query['id'] = {'$regex': workflow_type}
    
    workflows = vault.query('workflows', query)
    
    if not workflows:
        return {'message': 'No workflows found for analysis', 'period_days': days}
    
    # Calculate performance metrics
    total_workflows = len(workflows)
    completed_workflows = [w for w in workflows if w.get('status') == 'completed']
    completion_rate = (len(completed_workflows) / total_workflows) * 100
    
    # Calculate average execution time for completed workflows
    execution_times = []
    for workflow in completed_workflows:
        if 'completed_at' in workflow:
            start = datetime.fromisoformat(workflow['created_at'])
            end = datetime.fromisoformat(workflow['completed_at'])
            execution_times.append((end - start).total_seconds())
    
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    # Find most common failure points
    failure_steps = {}
    for workflow in workflows:
        if workflow.get('status') == 'failed':
            last_step = workflow.get('results', [])[-1] if workflow.get('results') else None
            if last_step:
                step_name = last_step.get('step', 'unknown')
                failure_steps[step_name] = failure_steps.get(step_name, 0) + 1
    
    # Performance by priority (for lead workflows)
    performance_by_priority = {}
    for workflow in workflows:
        priority = workflow.get('priority', 'unknown')
        if priority not in performance_by_priority:
            performance_by_priority[priority] = {'total': 0, 'completed': 0}
        performance_by_priority[priority]['total'] += 1
        if workflow.get('status') == 'completed':
            performance_by_priority[priority]['completed'] += 1
    
    return {
        'analysis_period_days': days,
        'total_workflows': total_workflows,
        'completion_rate': round(completion_rate, 2),
        'avg_execution_time_seconds': round(avg_execution_time, 2),
        'common_failure_steps': sorted(failure_steps.items(), key=lambda x: x[1], reverse=True)[:5],
        'performance_by_priority': performance_by_priority,
        'recommendations': generate_optimization_recommendations(workflows)
    }

def generate_optimization_recommendations(workflows: list) -> list:
    """Generate recommendations for workflow optimization"""
    recommendations = []
    
    # Check for consistently failing steps
    all_failures = {}
    for workflow in workflows:
        if workflow.get('status') == 'failed':
            for result in workflow.get('results', []):
                if not result.get('result', {}).get('success', True):
                    step = result.get('step')
                    all_failures[step] = all_failures.get(step, 0) + 1
    
    if all_failures:
        most_failing_step = max(all_failures.items(), key=lambda x: x[1])
        recommendations.append({
            'type': 'reliability',
            'priority': 'high',
            'message': f"Step '{most_failing_step[0]}' fails frequently ({most_failing_step[1]} times). Consider adding retry logic or error handling."
        })
    
    # Check for slow workflows
    slow_workflows = [w for w in workflows if w.get('status') == 'completed' and 
                     'completed_at' in w and 'created_at' in w]
    
    if slow_workflows:
        execution_times = []
        for w in slow_workflows:
            start = datetime.fromisoformat(w['created_at'])
            end = datetime.fromisoformat(w['completed_at'])
            execution_times.append((end - start).total_seconds())
        
        if execution_times and max(execution_times) > 3600:  # More than 1 hour
            recommendations.append({
                'type': 'performance',
                'priority': 'medium',
                'message': f"Some workflows take over 1 hour. Consider parallelizing steps or optimizing slow operations."
            })
    
    # Check completion rates
    completion_rate = len([w for w in workflows if w.get('status') == 'completed']) / len(workflows) * 100
    if completion_rate < 80:
        recommendations.append({
            'type': 'completion',
            'priority': 'high',
            'message': f"Low completion rate ({completion_rate:.1f}%). Review failed workflows and add better error handling."
        })
    
    return recommendations

# Tool 5: Scheduled Workflow Execution
@tool
def schedule_workflow_execution(workflow_type: str, schedule: str, params: dict = None) -> dict:
    """Schedule a workflow to run on a specific schedule"""
    
    schedule_id = f"schedule_{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    scheduled_task = {
        'id': schedule_id,
        'workflow_type': workflow_type,
        'schedule': schedule,  # e.g., 'daily', 'weekly', 'hourly'
        'params': params or {},
        'created_at': datetime.now().isoformat(),
        'last_run': None,
        'next_run': calculate_next_run_time(schedule),
        'status': 'active'
    }
    
    vault.store('scheduled_workflows', scheduled_task, key=schedule_id)
    
    return {
        'schedule_id': schedule_id,
        'workflow_type': workflow_type,
        'schedule': schedule,
        'next_run': scheduled_task['next_run'],
        'message': 'Workflow scheduled successfully'
    }

def calculate_next_run_time(schedule: str) -> str:
    """Calculate the next run time based on schedule"""
    now = datetime.now()
    
    if schedule == 'hourly':
        next_run = now + timedelta(hours=1)
    elif schedule == 'daily':
        next_run = now + timedelta(days=1)
    elif schedule == 'weekly':
        next_run = now + timedelta(weeks=1)
    elif schedule == 'monthly':
        next_run = now + timedelta(days=30)
    else:
        # Default to daily
        next_run = now + timedelta(days=1)
    
    return next_run.isoformat()

# Test the automation agent
def test_automation():
    """Test the automation agent with sample workflows"""
    print("🤖 Testing Workflow Automation Agent")
    print("=" * 50)
    
    # Test 1: Lead processing workflow
    print("\n1. Testing lead processing workflow...")
    sample_lead = {
        'id': 'lead_001',
        'name': 'John Smith',
        'email': 'john@techcorp.com',
        'company': 'TechCorp Inc',
        'role': 'CTO',
        'company_size': 500,
        'industry': 'technology',
        'downloaded_whitepaper': True,
        'requested_demo': True,
        'budget_indicated': 75000
    }
    
    response = automation.chat(f"Process this new lead: {json.dumps(sample_lead)}")
    print(f"Lead Processing: {response}")
    
    # Test 2: Order processing
    print("\n2. Testing order processing workflow...")
    sample_order = {
        'id': 'order_001',
        'customer_id': 'cust_123',
        'total': 1250.00,
        'shipping_country': 'Canada',
        'items': [
            {'id': 'item_1', 'name': 'Laptop', 'custom_engraving': True},
            {'id': 'item_2', 'name': 'Mouse', 'custom_engraving': False}
        ]
    }
    
    response = automation.chat(f"Process this order: {json.dumps(sample_order)}")
    print(f"Order Processing: {response}")
    
    # Test 3: Analytics
    print("\n3. Testing workflow analytics...")
    response = automation.chat("Analyze workflow performance for the last 7 days")
    print(f"Analytics: {response}")
    
    print("\n✅ Automation testing complete!")

# Deploy the automation agent
def deploy_automation():
    """Deploy the automation agent to production"""
    print("\n🚀 Deploying automation agent...")
    
    result = automation.deploy()
    
    print(f"✅ Automation agent deployed!")
    print(f"Deployment ID: {result['deployment_id']}")
    print(f"Namespace: {result['namespace']}")
    print(f"API endpoint: https://api.flowstack.fun/agents/{result['namespace']}/invoke")
    
    print("\n📝 Integration examples:")
    print("• Webhook for new leads: POST to endpoint with lead data")
    print("• Order processing: POST to endpoint with order data")
    print("• Scheduled execution: Set up cron jobs to trigger workflows")
    print("• Analytics API: GET requests for performance data")
    
    return result

if __name__ == "__main__":
    # Run tests
    test_automation()
    
    # Deploy
    deploy_choice = input("\nDeploy automation agent? (y/N): ")
    if deploy_choice.lower() == 'y':
        deploy_automation()
```

## Integration Examples

### Webhook for New Leads

```python title="lead_webhook.py"
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AUTOMATION_ENDPOINT = "https://api.flowstack.fun/agents/workflow-automation/invoke"
FLOWSTACK_API_KEY = "fs_your_api_key_here"

@app.route('/webhook/new-lead', methods=['POST'])
def handle_new_lead():
    """Handle new lead from your website form or CRM"""
    
    lead_data = request.json
    
    # Send to FlowStack automation agent
    response = requests.post(AUTOMATION_ENDPOINT,
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': FLOWSTACK_API_KEY
        },
        json={
            'message': f"Process this new lead: {json.dumps(lead_data)}"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        return jsonify({
            'status': 'success',
            'message': 'Lead processing workflow started',
            'workflow_info': result
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to start workflow'
        }), 500

if __name__ == '__main__':
    app.run(port=5000)
```

### Scheduled Workflow Runner

```python title="scheduler.py"
import schedule
import time
import requests
import json

AUTOMATION_ENDPOINT = "https://api.flowstack.fun/agents/workflow-automation/invoke"
FLOWSTACK_API_KEY = "fs_your_api_key_here"

def run_daily_analytics():
    """Run daily workflow analytics"""
    response = requests.post(AUTOMATION_ENDPOINT,
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': FLOWSTACK_API_KEY
        },
        json={
            'message': 'Analyze workflow performance for the last 24 hours and send report'
        }
    )
    print(f"Daily analytics result: {response.json()}")

def run_lead_nurture_sequence():
    """Trigger nurture sequence processing"""
    response = requests.post(AUTOMATION_ENDPOINT,
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': FLOWSTACK_API_KEY
        },
        json={
            'message': 'Process all pending nurture sequence emails'
        }
    )
    print(f"Nurture sequence result: {response.json()}")

# Schedule tasks
schedule.every().day.at("09:00").do(run_daily_analytics)
schedule.every().hour.do(run_lead_nurture_sequence)

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Advanced Workflow Patterns

### Conditional Branching

```python
@tool
def execute_conditional_workflow(data: dict, conditions: dict) -> dict:
    """Execute workflow with conditional branching"""
    
    workflow_id = f"conditional_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Evaluate conditions to determine path
    if conditions.get('customer_value') == 'high':
        workflow_path = 'vip_customer_path'
        steps = ['assign_account_manager', 'send_welcome_package', 'schedule_onboarding_call']
    elif conditions.get('product_interest') == 'enterprise':
        workflow_path = 'enterprise_sales_path'
        steps = ['qualify_enterprise_needs', 'generate_custom_proposal', 'schedule_demo']
    else:
        workflow_path = 'standard_path'
        steps = ['send_welcome_email', 'add_to_newsletter', 'schedule_followup']
    
    workflow = {
        'id': workflow_id,
        'path': workflow_path,
        'data': data,
        'conditions': conditions,
        'steps': steps,
        'current_step': 0,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat()
    }
    
    vault.store('conditional_workflows', workflow, key=workflow_id)
    
    return {
        'workflow_id': workflow_id,
        'selected_path': workflow_path,
        'steps': steps,
        'message': f'Conditional workflow started with path: {workflow_path}'
    }
```

### Parallel Execution

```python
@tool
def execute_parallel_workflow(tasks: list) -> dict:
    """Execute multiple workflow tasks in parallel"""
    
    workflow_id = f"parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create parallel task records
    parallel_tasks = []
    for i, task in enumerate(tasks):
        task_record = {
            'id': f"{workflow_id}_task_{i}",
            'task_data': task,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        parallel_tasks.append(task_record)
        vault.store('parallel_tasks', task_record, key=task_record['id'])
    
    workflow = {
        'id': workflow_id,
        'type': 'parallel',
        'total_tasks': len(tasks),
        'completed_tasks': 0,
        'failed_tasks': 0,
        'task_ids': [task['id'] for task in parallel_tasks],
        'status': 'in_progress',
        'created_at': datetime.now().isoformat()
    }
    
    vault.store('parallel_workflows', workflow, key=workflow_id)
    
    return {
        'workflow_id': workflow_id,
        'total_tasks': len(tasks),
        'task_ids': [task['id'] for task in parallel_tasks],
        'message': 'Parallel workflow started'
    }
```

### Error Handling and Retry Logic

```python
@tool
def execute_workflow_with_retry(workflow_id: str, max_retries: int = 3) -> dict:
    """Execute workflow step with retry logic for failed operations"""
    
    workflow = vault.retrieve('workflows', key=workflow_id)
    if not workflow:
        return {'error': 'Workflow not found'}
    
    current_step = workflow['steps'][workflow['current_step']]
    retry_count = workflow.get('retry_count', 0)
    
    try:
        # Attempt to execute step
        result = execute_step_action(current_step, workflow)
        
        if result.get('success'):
            # Success - move to next step
            workflow['current_step'] += 1
            workflow['retry_count'] = 0  # Reset retry count
            workflow['updated_at'] = datetime.now().isoformat()
            vault.store('workflows', workflow, key=workflow_id)
            
            return {
                'success': True,
                'step': current_step,
                'result': result,
                'next_step': workflow['steps'][workflow['current_step']] if workflow['current_step'] < len(workflow['steps']) else 'completed'
            }
        else:
            # Step failed - check if we should retry
            if retry_count < max_retries:
                workflow['retry_count'] = retry_count + 1
                workflow['last_retry_at'] = datetime.now().isoformat()
                vault.store('workflows', workflow, key=workflow_id)
                
                return {
                    'success': False,
                    'step': current_step,
                    'result': result,
                    'retry_count': workflow['retry_count'],
                    'max_retries': max_retries,
                    'message': f'Step failed, will retry ({workflow["retry_count"]}/{max_retries})'
                }
            else:
                # Max retries exceeded - mark workflow as failed
                workflow['status'] = 'failed'
                workflow['failed_at'] = datetime.now().isoformat()
                workflow['failure_reason'] = f'Step {current_step} failed after {max_retries} retries'
                vault.store('workflows', workflow, key=workflow_id)
                
                return {
                    'success': False,
                    'step': current_step,
                    'result': result,
                    'message': f'Workflow failed: Step {current_step} failed after {max_retries} retries'
                }
                
    except Exception as e:
        # Unexpected error
        workflow['status'] = 'error'
        workflow['error_at'] = datetime.now().isoformat()
        workflow['error_message'] = str(e)
        vault.store('workflows', workflow, key=workflow_id)
        
        return {
            'success': False,
            'step': current_step,
            'error': str(e),
            'message': 'Workflow encountered an unexpected error'
        }
```

## Performance Monitoring

### Workflow Dashboard

```python
@tool
def get_workflow_dashboard() -> dict:
    """Get real-time workflow dashboard data"""
    
    # Active workflows
    active_workflows = vault.query('workflows', {'status': 'in_progress'})
    
    # Failed workflows in last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    recent_failures = vault.query('workflows', {
        'status': 'failed',
        'failed_at': {'$gte': yesterday}
    })
    
    # Completion stats for last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_workflows = vault.query('workflows', {
        'created_at': {'$gte': week_ago}
    })
    
    completed_this_week = len([w for w in recent_workflows if w.get('status') == 'completed'])
    completion_rate = (completed_this_week / len(recent_workflows) * 100) if recent_workflows else 0
    
    # Workflow types breakdown
    workflow_types = {}
    for workflow in recent_workflows:
        wf_type = workflow['id'].split('_')[0]  # Extract type from ID
        workflow_types[wf_type] = workflow_types.get(wf_type, 0) + 1
    
    return {
        'active_workflows': len(active_workflows),
        'recent_failures': len(recent_failures),
        'weekly_completion_rate': round(completion_rate, 2),
        'total_workflows_this_week': len(recent_workflows),
        'workflow_types': workflow_types,
        'dashboard_updated_at': datetime.now().isoformat()
    }
```

## Next Steps

<div class="grid cards" markdown>

-   :material-memory:{ .lg .middle } **[Stateful Agent](stateful-agent.md)**

    ---

    Build agents that learn and adapt from every interaction

-   :material-swap-horizontal:{ .lg .middle } **[Multi-Provider Setup](multi-provider.md)**

    ---

    Optimize costs and capabilities across AI providers

-   :material-robot-excited:{ .lg .middle } **[Back to Chatbot](chatbot.md)**

    ---

    Build conversational interfaces for your workflows

</div>

---

!!! success "You Built a Workflow Automation Engine!"
    You've created an intelligent automation system that can handle complex, multi-step workflows with decision points, error handling, and state management. This goes far beyond simple automation tools like Zapier.

Your automation agent now has:
✅ **Intelligent Decision Making** - AI-driven workflow routing  
✅ **State Management** - Remembers progress across sessions  
✅ **Error Handling** - Retry logic and graceful failure handling  
✅ **Performance Analytics** - Track and optimize workflow efficiency  
✅ **Parallel Execution** - Handle multiple tasks simultaneously  
✅ **Conditional Logic** - Different paths based on data and context  