"""
Continuous Job Application System
Runs all job application bots in sequence, tracks progress, alerts on opportunities
"""
import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('continuous_job_hunter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Paths
CASCADE_PROJECTS = Path("C:/Users/denpo/CascadeProjects/my-first-ai-agent")
WORKSPACE = Path("C:/Users/denpo/.openclaw/workspace")

# Bot scripts to run
BOTS = [
    {
        'name': 'CrowdWorks',
        'script': CASCADE_PROJECTS / 'crowdworks_bot.py',
        'priority': 'high',
        'frequency': 'daily'
    },
    {
        'name': 'Lancers',
        'script': CASCADE_PROJECTS / 'lancers_bot.py',
        'priority': 'high',
        'frequency': 'daily'
    },
    {
        'name': 'Daijob',
        'script': CASCADE_PROJECTS / 'daijob_auto_reply.py',
        'priority': 'medium',
        'frequency': 'daily'
    },
    {
        'name': 'Forkwell',
        'script': CASCADE_PROJECTS / 'forkwell_bot.py',
        'priority': 'medium',
        'frequency': 'twice-daily'
    },
    {
        'name': 'LinkedIn',
        'script': CASCADE_PROJECTS / 'linkedin_bot.py',
        'priority': 'high',
        'frequency': 'twice-daily'
    },
    {
        'name': 'Findy',
        'script': CASCADE_PROJECTS / 'findy_bot.py',
        'priority': 'medium',
        'frequency': 'daily'
    }
]

# Also check for new messages to reply to
MESSAGE_CHECKERS = [
    {
        'name': 'CrowdWorks Messages',
        'script': WORKSPACE / 'crowdworks_auto_handler.py',
        'priority': 'high',
        'frequency': 'hourly'
    },
    {
        'name': 'Gmail Job Emails',
        'script': WORKSPACE / 'gmail_job_reply_bot.py',
        'priority': 'high',
        'frequency': 'hourly'
    }
]

STATS_FILE = WORKSPACE / 'job_hunt_stats.json'


def load_stats():
    """Load job hunting statistics."""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        'total_applications': 0,
        'total_responses': 0,
        'interviews_scheduled': 0,
        'platforms': {},
        'last_run': None,
        'started_at': datetime.now().isoformat()
    }


def save_stats(stats):
    """Save job hunting statistics."""
    stats['last_run'] = datetime.now().isoformat()
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def run_bot(bot):
    """Run a job application bot."""
    log.info(f"\n{'='*60}")
    log.info(f"Running: {bot['name']}")
    log.info(f"{'='*60}")
    
    if not bot['script'].exists():
        log.warning(f"Script not found: {bot['script']}")
        return {'success': False, 'reason': 'script_not_found'}
    
    try:
        result = subprocess.run(
            [sys.executable, str(bot['script'])],
            cwd=bot['script'].parent,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        log.info(f"Exit code: {result.returncode}")
        
        if result.stdout:
            log.info(f"Output:\n{result.stdout}")
        
        if result.stderr:
            log.warning(f"Errors:\n{result.stderr}")
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        log.error(f"Timeout running {bot['name']}")
        return {'success': False, 'reason': 'timeout'}
    except Exception as e:
        log.error(f"Error running {bot['name']}: {e}")
        return {'success': False, 'reason': str(e)}


def parse_bot_results(bot_name, output):
    """Parse bot output to extract statistics."""
    stats = {
        'applications': 0,
        'responses': 0,
        'interviews': 0
    }
    
    # Look for common patterns in bot output
    if 'applied' in output.lower() or 'submitted' in output.lower():
        # Try to extract numbers
        import re
        matches = re.findall(r'(\d+)\s+(?:application|applied|submitted)', output.lower())
        if matches:
            stats['applications'] = int(matches[0])
    
    if 'interview' in output.lower():
        matches = re.findall(r'(\d+)\s+interview', output.lower())
        if matches:
            stats['interviews'] = int(matches[0])
    
    return stats


def run_all_bots(mode='full'):
    """Run all job application bots."""
    log.info(f"\n{'#'*60}")
    log.info(f"Starting Continuous Job Application Run")
    log.info(f"Mode: {mode}")
    log.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"{'#'*60}\n")
    
    stats = load_stats()
    session_stats = {
        'applications': 0,
        'responses': 0,
        'interviews': 0,
        'platforms_run': 0,
        'platforms_success': 0,
        'platforms_failed': 0
    }
    
    # Run application bots
    for bot in BOTS:
        result = run_bot(bot)
        session_stats['platforms_run'] += 1
        
        if result['success']:
            session_stats['platforms_success'] += 1
            
            # Parse results
            bot_stats = parse_bot_results(bot['name'], result.get('output', ''))
            session_stats['applications'] += bot_stats['applications']
            session_stats['interviews'] += bot_stats['interviews']
            
            # Update platform-specific stats
            if bot['name'] not in stats['platforms']:
                stats['platforms'][bot['name']] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'applications': 0
                }
            
            stats['platforms'][bot['name']]['total_runs'] += 1
            stats['platforms'][bot['name']]['successful_runs'] += 1
            stats['platforms'][bot['name']]['applications'] += bot_stats['applications']
        else:
            session_stats['platforms_failed'] += 1
            log.warning(f"{bot['name']} failed: {result.get('reason', 'unknown')}")
    
    # Run message checkers
    log.info(f"\n{'='*60}")
    log.info("Checking for messages to reply to...")
    log.info(f"{'='*60}")
    
    for checker in MESSAGE_CHECKERS:
        result = run_bot(checker)
        if result['success']:
            # Parse responses
            bot_stats = parse_bot_results(checker['name'], result.get('output', ''))
            session_stats['responses'] += bot_stats['responses']
    
    # Update overall stats
    stats['total_applications'] += session_stats['applications']
    stats['total_responses'] += session_stats['responses']
    stats['interviews_scheduled'] += session_stats['interviews']
    
    save_stats(stats)
    
    # Summary
    log.info(f"\n{'#'*60}")
    log.info("Session Summary:")
    log.info(f"  Applications sent: {session_stats['applications']}")
    log.info(f"  Responses handled: {session_stats['responses']}")
    log.info(f"  Interviews found: {session_stats['interviews']}")
    log.info(f"  Platforms run: {session_stats['platforms_run']}")
    log.info(f"  Success: {session_stats['platforms_success']}")
    log.info(f"  Failed: {session_stats['platforms_failed']}")
    log.info(f"\nOverall Stats (Since {stats['started_at']}):")
    log.info(f"  Total applications: {stats['total_applications']}")
    log.info(f"  Total responses: {stats['total_responses']}")
    log.info(f"  Interviews scheduled: {stats['interviews_scheduled']}")
    log.info(f"{'#'*60}\n")
    
    return session_stats


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    run_all_bots(mode)
