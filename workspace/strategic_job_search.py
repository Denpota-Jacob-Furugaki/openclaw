"""
Strategic Job Search Based on Freelance Market Dashboard Insights
Uses market intelligence to target high-value niches and platforms
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Market Intelligence from Dashboard
TOP_NICHES = [
    {
        'title': 'AI workflow builder for SMEs',
        'demand': 'Very high',
        'competition': 'Medium',
        'keywords': ['AI', 'automation', 'workflow', 'integration', 'ChatGPT', 'OpenAI', 'LLM'],
        'platforms': ['CrowdWorks', 'Lancers', 'LinkedIn'],
        'value_proposition': 'AI audit + implementation for support, reporting, search, CRM ops'
    },
    {
        'title': 'Data and analytics engineer',
        'demand': 'High',
        'competition': 'Medium',
        'keywords': ['data', 'analytics', 'BI', 'dashboard', 'ETL', 'warehouse', 'BigQuery', 'Tableau'],
        'platforms': ['Forkwell', 'LinkedIn', 'CrowdWorks'],
        'value_proposition': 'Warehouse setup, ETL, BI dashboards, monthly decision reviews'
    },
    {
        'title': 'Cloud and platform reliability partner',
        'demand': 'High',
        'competition': 'Low',
        'keywords': ['cloud', 'AWS', 'GCP', 'Azure', 'DevOps', 'observability', 'cost optimization'],
        'platforms': ['LinkedIn', 'Forkwell'],
        'value_proposition': 'Migration, observability, performance tuning, platform cost control'
    },
    {
        'title': 'Security-conscious app engineer',
        'demand': 'High',
        'competition': 'Low',
        'keywords': ['security', 'auth', 'compliance', 'GDPR', 'permissions', 'audit'],
        'platforms': ['Forkwell', 'LinkedIn'],
        'value_proposition': 'Secure implementation, auth hardening, AI risk controls'
    },
    {
        'title': 'Product engineer with revenue ownership',
        'demand': 'High',
        'competition': 'High',
        'keywords': ['product', 'growth', 'conversion', 'React', 'TypeScript', 'full-stack'],
        'platforms': ['CrowdWorks', 'Lancers', 'Forkwell'],
        'value_proposition': 'Launch faster, reduce manual workload, improve conversion'
    }
]

# Denpota's profile mapped to niches
DENPOTA_NICHE_FIT = {
    'AI workflow builder': {
        'match': 95,
        'reasoning': 'Strong AI/ML experience (OpenAI, TensorFlow), JavaScript/TypeScript for integration',
        'proof_points': [
            'Built multiple AI automation bots (job search, email replies)',
            'OpenAI API integration experience',
            'Full-stack capability (React + Node.js)'
        ]
    },
    'Product engineer with revenue ownership': {
        'match': 90,
        'reasoning': 'Marketing + dev background, proven ROI metrics',
        'proof_points': [
            'Onitsuka Tiger 17 countries ROAS 120%',
            'Meta Q1 Top Performer #1/34',
            'Full-stack development (React/Next.js, Node.js)'
        ]
    },
    'Data and analytics engineer': {
        'match': 75,
        'reasoning': 'Marketing analytics experience, data-driven approach',
        'proof_points': [
            'Google/META Ads analytics',
            'InsightHub task efficiency tracking',
            'Data-driven marketing decisions'
        ]
    }
}

PLATFORM_STRATEGY = {
    'CrowdWorks': {
        'priority': 'High',
        'use_for': 'AI automation projects, Japan SME demand',
        'search_keywords': ['AI', '自動化', 'ChatGPT', 'LLM', 'API連携', 'ワークフロー'],
        'positioning': 'AI automation specialist for business workflows'
    },
    'Lancers': {
        'priority': 'High',
        'use_for': 'AI-related work, business building support',
        'search_keywords': ['AI', '機械学習', 'ChatGPT', 'データ分析', 'マーケティング'],
        'positioning': 'AI + marketing engineering specialist'
    },
    'Forkwell': {
        'priority': 'Medium',
        'use_for': 'Engineering-specific roles, credibility building',
        'search_keywords': ['React', 'TypeScript', 'Node.js', 'AI', 'full-stack'],
        'positioning': 'Full-stack engineer with AI/marketing background'
    },
    'LinkedIn': {
        'priority': 'High',
        'use_for': 'Global remote, higher-ticket work',
        'search_keywords': ['AI implementation', 'marketing engineering', 'growth engineering'],
        'positioning': 'AI-enabled product engineer with proven revenue impact'
    }
}

def generate_search_strategy():
    """Generate targeted search strategy based on market intelligence."""
    
    strategy = {
        'generated_at': datetime.now().isoformat(),
        'top_3_niches': [],
        'platform_priorities': {},
        'search_terms': {},
        'value_propositions': {},
        'application_targets': {}
    }
    
    # Rank niches by Denpota's fit
    ranked_niches = sorted(
        DENPOTA_NICHE_FIT.items(),
        key=lambda x: x[1]['match'],
        reverse=True
    )
    
    strategy['top_3_niches'] = [
        {
            'niche': niche,
            'match_score': data['match'],
            'reasoning': data['reasoning'],
            'proof_points': data['proof_points']
        }
        for niche, data in ranked_niches[:3]
    ]
    
    # Platform-specific strategies
    for platform, config in PLATFORM_STRATEGY.items():
        strategy['platform_priorities'][platform] = config['priority']
        strategy['search_terms'][platform] = config['search_keywords']
        strategy['value_propositions'][platform] = config['positioning']
    
    # Application targets per platform
    strategy['application_targets'] = {
        'CrowdWorks': {
            'daily_target': 5,
            'focus': 'AI automation, workflow integration, ChatGPT projects',
            'filters': ['リモート', 'AI', '自動化', 'フルスタック']
        },
        'Lancers': {
            'daily_target': 5,
            'focus': 'AI implementation, marketing + tech hybrid',
            'filters': ['AI', 'マーケティング', 'リモート', '開発']
        },
        'Forkwell': {
            'daily_target': 3,
            'focus': 'Engineering roles with product ownership',
            'filters': ['React', 'TypeScript', 'AI', 'リモート']
        },
        'LinkedIn': {
            'daily_target': 3,
            'focus': 'Global remote, AI implementation, growth engineering',
            'filters': ['AI implementation', 'remote', 'growth engineering']
        }
    }
    
    return strategy

def generate_positioning_statement():
    """Generate elevator pitch based on market positioning."""
    
    japanese = """私は、AIワークフロー実装とマーケティングエンジニアリングを専門とするフリーランス開発者です。

【強み】
・AI自動化システムの実装（OpenAI API、ChatGPT統合）
・フルスタック開発（React/Next.js + Node.js + Python）
・マーケティング×技術のハイブリッド経験

【実績】
・Onitsuka Tiger 17ヶ国展開 ROAS 120%達成
・Meta社 Q1パフォーマンス1位/34名
・複数のAI自動化ボット開発（求人応募、メール返信）

【提供価値】
ビジネスワークフローへのAI導入・自動化から、データドリブンな成長施策まで、技術とビジネス成果を繋ぐエンジニアリングを提供します。

ポートフォリオ：https://denpota-portfolio.vercel.app/"""

    english = """I'm a freelance software engineer specializing in AI workflow implementation and marketing engineering.

**Strengths:**
- AI automation system implementation (OpenAI API, ChatGPT integration)
- Full-stack development (React/Next.js + Node.js + Python)
- Hybrid marketing × technical expertise

**Track Record:**
- Onitsuka Tiger 17-country expansion: 120% ROAS
- Meta Q1 Top Performer #1/34
- Multiple AI automation bots (job applications, email responses)

**Value Delivery:**
From AI integration into business workflows to data-driven growth initiatives, I bridge technical execution and measurable business outcomes.

Portfolio: https://denpota-portfolio.vercel.app/"""
    
    return {'japanese': japanese, 'english': english}

def main():
    """Generate and save strategic job search plan."""
    
    print("="*60)
    print("STRATEGIC JOB SEARCH PLAN")
    print("Based on Freelance Market Dashboard Intelligence")
    print("="*60)
    
    strategy = generate_search_strategy()
    positioning = generate_positioning_statement()
    
    # Save strategy
    output_file = Path('strategic_job_search_plan.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'strategy': strategy,
            'positioning': positioning
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Strategy saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("TOP 3 NICHE MATCHES FOR DENPOTA:")
    print("="*60)
    
    for i, niche in enumerate(strategy['top_3_niches'], 1):
        print(f"\n{i}. {niche['niche']} (Match: {niche['match_score']}%)")
        print(f"   {niche['reasoning']}")
        print(f"   Proof: {', '.join(niche['proof_points'][:2])}")
    
    print("\n" + "="*60)
    print("PLATFORM STRATEGY:")
    print("="*60)
    
    for platform, priority in strategy['platform_priorities'].items():
        if priority == 'High':
            target = strategy['application_targets'].get(platform, {})
            print(f"\n{platform} ({priority} Priority)")
            print(f"  Daily target: {target.get('daily_target', 'N/A')} applications")
            print(f"  Focus: {target.get('focus', 'N/A')}")
    
    print("\n" + "="*60)
    print("VALUE PROPOSITION (JAPANESE):")
    print("="*60)
    print(positioning['japanese'])
    
    print("\n" + "="*60)
    
    return strategy, positioning

if __name__ == "__main__":
    main()
