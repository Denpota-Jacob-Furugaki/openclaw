"""
Update all job bots with new strategic positioning
Prioritizes: AI workflow builder + marketing engineer niches
"""
import json
from pathlib import Path

# New strategic configuration
STRATEGIC_CONFIG = {
    "positioning": {
        "primary_niche": "AI Workflow Builder",
        "secondary_niche": "Product Engineer with Revenue Ownership",
        "value_prop_japanese": """私は、AIワークフロー実装とマーケティングエンジニアリングを専門とするフリーランス開発者です。

【強み】
・AI自動化システムの実装（OpenAI API、ChatGPT統合）
・フルスタック開発（React/Next.js + Node.js + Python）
・マーケティング×技術のハイブリッド経験

【実績】
・Onitsuka Tiger 17ヶ国展開 ROAS 120%達成
・Meta社 Q1パフォーマンス1位/34名
・複数のAI自動化ボット開発

【提供価値】
ビジネスワークフローへのAI導入・自動化から、データドリブンな成長施策まで、技術とビジネス成果を繋ぐエンジニアリングを提供します。

ポートフォリオ：https://denpota-portfolio.vercel.app/""",
        "value_prop_english": """I'm a freelance software engineer specializing in AI workflow implementation and marketing engineering.

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
    },
    "platform_strategies": {
        "CrowdWorks": {
            "daily_target": 5,
            "priority": "HIGH",
            "search_keywords": ["AI", "自動化", "ChatGPT", "LLM", "API連携", "ワークフロー", "機械学習", "OpenAI"],
            "positioning": "AI automation specialist for business workflows",
            "filters": {
                "remote": True,
                "keywords_include": ["AI", "自動化", "ワークフロー", "ChatGPT", "API"],
                "keywords_exclude": ["営業", "事務", "単純作業"]
            }
        },
        "Lancers": {
            "daily_target": 5,
            "priority": "HIGH",
            "search_keywords": ["AI", "機械学習", "ChatGPT", "データ分析", "マーケティング", "自動化"],
            "positioning": "AI + marketing engineering specialist",
            "filters": {
                "remote": True,
                "keywords_include": ["AI", "マーケティング", "分析", "自動化"],
                "keywords_exclude": ["営業", "事務"]
            }
        },
        "LinkedIn": {
            "daily_target": 3,
            "priority": "HIGH",
            "search_keywords": ["AI implementation", "marketing engineering", "growth engineering", "AI workflow", "automation"],
            "positioning": "AI-enabled product engineer with proven revenue impact",
            "filters": {
                "remote": True,
                "keywords_include": ["AI", "remote", "automation", "growth"],
                "keywords_exclude": ["sales", "admin"]
            }
        },
        "Forkwell": {
            "daily_target": 3,
            "priority": "MEDIUM",
            "search_keywords": ["React", "TypeScript", "Node.js", "AI", "full-stack", "機械学習"],
            "positioning": "Full-stack engineer with AI/marketing background",
            "filters": {
                "remote": True,
                "keywords_include": ["React", "TypeScript", "AI", "リモート"],
                "keywords_exclude": []
            }
        },
        "Findy": {
            "daily_target": 2,
            "priority": "MEDIUM",
            "search_keywords": ["AI", "機械学習", "フルスタック", "TypeScript", "React"],
            "positioning": "AI workflow engineer",
            "filters": {
                "remote": True,
                "keywords_include": ["AI", "フルスタック", "リモート"],
                "keywords_exclude": []
            }
        },
        "Daijob": {
            "daily_target": 2,
            "priority": "MEDIUM",
            "search_keywords": ["AI", "software engineer", "full-stack", "marketing engineer"],
            "positioning": "AI + marketing specialist",
            "filters": {
                "remote": True,
                "keywords_include": ["AI", "remote", "engineer"],
                "keywords_exclude": ["sales only"]
            }
        }
    },
    "total_daily_target": 20,
    "focus_areas": [
        "AI workflow implementation",
        "ChatGPT/LLM integration",
        "Marketing automation",
        "Growth engineering",
        "Product engineering with ROI focus"
    ]
}

def save_config():
    """Save strategic configuration."""
    output_file = Path('strategic_bot_config.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(STRATEGIC_CONFIG, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Strategic configuration saved to: {output_file}")
    return output_file

def update_continuous_hunter():
    """Update continuous job hunter with new targets."""
    print("\n" + "="*60)
    print("STRATEGIC UPDATE SUMMARY")
    print("="*60)
    
    print(f"\nPrimary Positioning: {STRATEGIC_CONFIG['positioning']['primary_niche']}")
    print(f"Total Daily Target: {STRATEGIC_CONFIG['total_daily_target']} applications")
    
    print("\nPlatform Breakdown:")
    for platform, config in STRATEGIC_CONFIG['platform_strategies'].items():
        print(f"  {platform:12} {config['priority']:6} - {config['daily_target']} apps/day - {config['positioning']}")
    
    print("\nFocus Areas:")
    for area in STRATEGIC_CONFIG['focus_areas']:
        print(f"  • {area}")
    
    print("\n" + "="*60)
    print("Configuration is ready for use by all job bots!")
    print("="*60)

if __name__ == "__main__":
    config_file = save_config()
    update_continuous_hunter()
    
    print("\n✓ All bots updated with strategic positioning!")
    print("✓ Next run will use new keywords and targeting")
    print("✓ Positioned as: AI Workflow Builder + Marketing Engineer")
