"""
Sample data for AgentBear News
Create sample articles to demonstrate the news site
"""

from news_database import NewsDatabase
from datetime import datetime

def create_sample_data():
    db = NewsDatabase()
    
    # Sample article 1: Featured
    article1 = {
        'slug': 'openai-gpt-5-preview-enterprise-impact',
        'title': "OpenAI Quietly Previewed GPT-5 to Enterprise Customers. Here's What We Know.",
        'subtitle': 'The next generation is coming sooner than expected — and the implications for businesses are massive.',
        'content': '''
        <p>OpenAI held private briefings with select enterprise customers last week, showing early demos of what they're calling "the next major leap." While officially unnamed, sources confirm this is GPT-5.</p>
        
        <h2>What Was Shown</h2>
        
        <p>According to attendees, the new model demonstrates:</p>
        
        <ul>
        <li>Significantly improved reasoning capabilities — solving complex multi-step problems that stumped GPT-4</li>
        <li>Near-perfect code generation with context awareness across entire codebases</li>
        <li>Multimodal understanding that actually works — seamlessly processing documents, images, and audio together</li>
        <li>Enterprise features: audit logs, data residency options, and fine-tuning controls</li>
        </ul>
        
        <h2>The Timeline</h2>
        
        <p>Multiple sources suggest a public release could come as early as Q2 2026, with enterprise access potentially sooner. This is significantly faster than the GPT-3 to GPT-4 gap.</p>
        
        <p>Why the rush? Competition. Google's Gemini 2.5 is gaining ground, and Anthropic's Claude continues to win on reliability. OpenAI needs a win.</p>
        
        <h2>The Enterprise Angle</h2>
        
        <p>Here's what caught my attention: OpenAI is prioritizing enterprise features over consumer shiny objects.</p>
        
        <p>They know where the money is. Consumers are fickle. Enterprises pay $20/seat/month and stick around.</p>
        
        <p>The demo reportedly included:</p>
        
        <ul>
        <li>Automated compliance checking for regulated industries</li>
        <li>Integration with existing enterprise security stacks</li>
        <li>SLA guarantees for the first time</li>
        </ul>
        
        <h2>What This Means for Infrastructure</h2>
        
        <p>As someone who's spent 20 years in storage and infrastructure, I see the writing on the wall.</p>
        
        <p>Enterprise AI workloads are about to explode. GPT-5's reasoning capabilities mean companies will actually trust it with production workflows. Not just chatbots — actual business processes.</p>
        
        <p>If your infrastructure team isn't preparing for 10x AI compute demand, you're already behind.</p>
        ''',
        'summary': 'OpenAI previewed GPT-5 to enterprise customers with major improvements in reasoning, code generation, and multimodal understanding. Enterprise release could come Q2 2026.',
        'source_url': 'https://openai.com',
        'source_name': 'Industry Briefing',
        'category': 'industry',
        'tags': ['openai', 'gpt-5', 'enterprise', 'ai-infrastructure'],
        'featured': True,
        'published_at': datetime.now().isoformat()
    }
    
    # Sample article 2
    article2 = {
        'slug': 'ai-agent-orchestration-2026-landscape',
        'title': 'The AI Agent Orchestration Wars Have Begun',
        'subtitle': 'Why 2026 will be remembered as the year agents stopped being toys and started getting real work done.',
        'content': '''
        <p>Remember when "AI agent" meant a chatbot that could book a restaurant? Those days are over.</p>
        
        <p>We're now seeing agents that can:</p>
        
        <ul>
        <li>Research, write, and publish entire technical documentation</li>
        <li>Debug production code across multiple services</li>
        <li>Negotiate with other agents to complete complex multi-party tasks</li>
        </ul>
        
        <h2>The Orchestration Layer</h2>
        
        <p>The big players know the money isn't in individual agents. It's in orchestrating armies of them.</p>
        
        <p>Microsoft's Copilot Studio, Google's Vertex AI Agent Builder, and Amazon's Bedrock Agents are all racing to own the orchestration layer.</p>
        
        <h2>The Storage Problem Nobody Talks About</h2>
        
        <p>Here's what the infrastructure folks are realizing: these agents generate *data*. Lots of it.</p>
        
        <p>Every agent interaction, every decision tree, every rollback — it's all data that needs to be stored, indexed, and searchable. For compliance, for debugging, for improvement.</p>
        
        <p>Traditional log management isn't built for this scale. We're talking petabytes of structured agent telemetry.</p>
        ''',
        'summary': 'AI agents are moving from demos to production, with major cloud providers battling for the orchestration layer. Infrastructure challenges around data storage are emerging.',
        'source_url': 'https://azure.microsoft.com',
        'source_name': 'Cloud Providers',
        'category': 'agents',
        'tags': ['ai-agents', 'orchestration', 'microsoft', 'google', 'aws'],
        'featured': False,
        'published_at': datetime.now().isoformat()
    }
    
    # Create articles
    try:
        db.create_article(article1)
        print(f"✅ Created featured article: {article1['title']}")
    except Exception as e:
        print(f"⚠️ Article 1 may already exist: {e}")
    
    try:
        db.create_article(article2)
        print(f"✅ Created article: {article2['title']}")
    except Exception as e:
        print(f"⚠️ Article 2 may already exist: {e}")
    
    print("\n📊 Stats:", db.get_stats())

if __name__ == '__main__':
    create_sample_data()
