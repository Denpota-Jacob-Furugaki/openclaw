#!/usr/bin/env python3
"""
OpenClaw Telegram Bot
Provides notifications and remote control for OpenClaw deployment
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Optional
import requests

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        ContextTypes,
        MessageHandler,
        filters
    )
except ImportError:
    print("Please install python-telegram-bot: pip install python-telegram-bot")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'telegram-config.json')
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

BOT_TOKEN = config['bot']['token']
ADMIN_CHAT_ID = config['admin'].get('chat_id')
ADMIN_PHONE = config['admin']['phone']

# Docker compose path
DOCKER_COMPOSE_PATH = os.path.join(os.path.dirname(__file__), 'docker-compose.yml')


class OpenClawBot:
    """Main bot class for OpenClaw management"""
    
    def __init__(self):
        self.app = None
        self.authorized_users = set()
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "YOUR_CHAT_ID_HERE":
            try:
                self.authorized_users.add(int(ADMIN_CHAT_ID))
            except (ValueError, TypeError):
                logger.warning(f"Invalid ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id in self.authorized_users or len(self.authorized_users) == 0
    
    async def authorize_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Authorize a new user"""
        user_id = update.effective_user.id
        if user_id not in self.authorized_users:
            self.authorized_users.add(user_id)
            logger.info(f"Authorized user: {user_id} ({update.effective_user.username})")
            await update.message.reply_text(
                "✅ You have been authorized to use this bot.\n"
                f"Your Chat ID: {user_id}\n"
                "Add this to telegram-config.json for persistent access."
            )
        else:
            await update.message.reply_text("✅ You are already authorized.")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        welcome_message = f"""
🤖 **OpenClaw Bot**

Welcome {update.effective_user.first_name}!

Your Chat ID: `{user_id}`
Username: @{username}

**Available Commands:**
/status - Check system status
/logs - View recent logs
/metrics - System metrics
/restart - Restart services
/stop - Stop services
/start - Start services
/health - Health check
/authorize - Authorize this chat
/help - Show this help

Use /authorize to enable bot access if needed.
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
        # Auto-authorize if admin phone matches
        if ADMIN_CHAT_ID is None:
            self.authorized_users.add(user_id)
            logger.info(f"Auto-authorized first user: {user_id}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check OpenClaw status"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("🔍 Checking status...")
        
        try:
            result = subprocess.run(
                ['docker-compose', 'ps'],
                cwd=os.path.dirname(DOCKER_COMPOSE_PATH),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            status_message = f"**Container Status:**\n```\n{result.stdout}\n```"
            await update.message.reply_text(status_message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View recent logs"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        service = context.args[0] if context.args else 'openclaw'
        lines = config['settings']['log_lines']
        
        await update.message.reply_text(f"📋 Fetching {service} logs...")
        
        try:
            result = subprocess.run(
                ['docker-compose', 'logs', '--tail', str(lines), service],
                cwd=os.path.dirname(DOCKER_COMPOSE_PATH),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            logs = result.stdout[-4000:] if len(result.stdout) > 4000 else result.stdout
            await update.message.reply_text(f"```\n{logs}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Restart services"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        service = context.args[0] if context.args else None
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"restart_{service or 'all'}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔄 Restart {service or 'all services'}?",
            reply_markup=reply_markup
        )
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system metrics"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📊 Collecting metrics...")
        
        try:
            # Docker stats
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format',
                 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            metrics = f"**System Metrics:**\n```\n{result.stdout}\n```"
            await update.message.reply_text(metrics, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Health check"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("🏥 Running health check...")
        
        checks = {
            "OpenClaw": "http://localhost:8080/health",
            "Ollama": "http://localhost:11434/",
        }
        
        results = []
        for name, url in checks.items():
            try:
                response = requests.get(url, timeout=5)
                status = "✅" if response.status_code == 200 else "⚠️"
                results.append(f"{status} {name}: {response.status_code}")
            except Exception as e:
                results.append(f"❌ {name}: {str(e)[:50]}")
        
        health_message = "**Health Check Results:**\n" + "\n".join(results)
        await update.message.reply_text(health_message)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_authorized(query.from_user.id):
            await query.edit_message_text("⛔ Unauthorized.")
            return
        
        action = query.data
        
        if action == "cancel":
            await query.edit_message_text("❌ Cancelled")
            return
        
        if action.startswith("restart_"):
            service = action.split("_")[1]
            await query.edit_message_text(f"🔄 Restarting {service}...")
            
            try:
                cmd = ['docker-compose', 'restart']
                if service != 'all':
                    cmd.append(service)
                
                subprocess.run(
                    cmd,
                    cwd=os.path.dirname(DOCKER_COMPOSE_PATH),
                    timeout=30
                )
                await query.edit_message_text(f"✅ Restarted {service}")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        help_text = """
**OpenClaw Bot Commands:**

📊 **Monitoring:**
/status - Container status
/logs [service] - View logs
/metrics - Resource usage
/health - Health checks

🎮 **Control:**
/restart [service] - Restart
/stop [service] - Stop
/start [service] - Start

📧 **Google:**
/gmail - Check inbox (last 5 emails)
/email [id] - Read full email
/calendar - Upcoming events
/acceptall - Accept all pending calendar invites
/sheets - List spreadsheets
/drive - Recent Drive files

ℹ️ **Info:**
/help - This help
/authorize - Authorize access

**Examples:**
`/logs openclaw`
`/restart ollama`
`/gmail`
`/calendar`
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def gmail_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check Gmail inbox"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📧 Checking Gmail inbox...")
        
        try:
            from google_gmail import search_emails, get_unread_count
            
            emails = search_emails(query='', max_results=5)
            unread = get_unread_count()
            
            message = f"**Gmail Inbox** ({unread} unread)\n\n"
            
            for i, email in enumerate(emails, 1):
                subject = email['subject'][:50]
                from_addr = email['from'].split('<')[0].strip()[:30]
                snippet = email['snippet'][:60]
                
                message += f"{i}. **{subject}**\n"
                message += f"   From: {from_addr}\n"
                message += f"   {snippet}...\n"
                message += f"   ID: `{email['id']}`\n\n"
            
            message += "\nUse `/email [id]` to read full email"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Gmail error: {str(e)}")
    
    async def email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Read full email"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /email [message_id]")
            return
        
        message_id = context.args[0]
        await update.message.reply_text("📧 Reading email...")
        
        try:
            from google_gmail import get_email_full
            
            email = get_email_full(message_id)
            
            body = email['body'][:2000] if len(email['body']) > 2000 else email['body']
            
            message = f"**From:** {email['from']}\n"
            message += f"**To:** {email['to']}\n"
            message += f"**Date:** {email['date']}\n"
            message += f"**Subject:** {email['subject']}\n\n"
            message += f"```\n{body}\n```"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading email: {str(e)}")
    
    async def calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View upcoming calendar events"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📅 Checking calendar...")
        
        try:
            from google_calendar import get_upcoming_events, get_pending_invites
            
            events = get_upcoming_events(days_ahead=7, max_results=5)
            pending = get_pending_invites()
            
            message = f"**Upcoming Events** (Next 7 days)\n\n"
            
            if not events:
                message += "No upcoming events.\n"
            else:
                for event in events:
                    summary = event['summary'][:50]
                    start = event['start'].split('T')[0] if 'T' in event['start'] else event['start']
                    
                    message += f"📅 **{summary}**\n"
                    message += f"   {start}\n"
                    if event['location']:
                        message += f"   📍 {event['location'][:40]}\n"
                    message += "\n"
            
            if pending:
                message += f"\n⏳ **{len(pending)} Pending Invite(s)**\n"
                message += "Use /acceptall to accept them\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Calendar error: {str(e)}")
    
    async def acceptall_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Accept all pending calendar invites"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📅 Accepting all pending invites...")
        
        try:
            from google_calendar import accept_all_pending
            
            count = accept_all_pending()
            
            await update.message.reply_text(f"✅ Accepted {count} calendar invite(s)")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def sheets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List Google Spreadsheets"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📊 Listing spreadsheets...")
        
        try:
            from google_drive import search_files
            
            sheets = search_files(file_type='spreadsheet')[:5]
            
            if not sheets:
                await update.message.reply_text("No spreadsheets found.")
                return
            
            message = "**Your Spreadsheets**\n\n"
            
            for sheet in sheets:
                name = sheet['name'][:50]
                sheet_id = sheet['id']
                
                message += f"📊 **{name}**\n"
                message += f"   ID: `{sheet_id}`\n"
                if sheet.get('webViewLink'):
                    message += f"   [Open]({sheet['webViewLink']})\n"
                message += "\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def drive_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List recent Google Drive files"""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized. Use /authorize first.")
            return
        
        await update.message.reply_text("📁 Listing recent files...")
        
        try:
            from google_drive import list_files
            
            files = list_files(max_results=10)
            
            if not files:
                await update.message.reply_text("No files found.")
                return
            
            message = "**Recent Drive Files**\n\n"
            
            for file in files:
                name = file['name'][:40]
                file_type = file['mimeType'].split('.')[-1]
                
                icon = "📄"
                if "spreadsheet" in file['mimeType']:
                    icon = "📊"
                elif "document" in file['mimeType']:
                    icon = "📝"
                elif "folder" in file['mimeType']:
                    icon = "📁"
                
                message += f"{icon} **{name}**\n"
                if file.get('webViewLink'):
                    message += f"   [Open]({file['webViewLink']})\n"
                message += "\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"❌ An error occurred: {str(context.error)[:200]}"
            )
    
    def run(self):
        """Start the bot"""
        logger.info("Starting OpenClaw Telegram Bot...")
        
        # Create application
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("logs", self.logs_command))
        self.app.add_handler(CommandHandler("restart", self.restart_command))
        self.app.add_handler(CommandHandler("metrics", self.metrics_command))
        self.app.add_handler(CommandHandler("health", self.health_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("authorize", self.authorize_user))
        
        # Google integration handlers
        self.app.add_handler(CommandHandler("gmail", self.gmail_command))
        self.app.add_handler(CommandHandler("email", self.email_command))
        self.app.add_handler(CommandHandler("calendar", self.calendar_command))
        self.app.add_handler(CommandHandler("acceptall", self.acceptall_command))
        self.app.add_handler(CommandHandler("sheets", self.sheets_command))
        self.app.add_handler(CommandHandler("drive", self.drive_command))
        
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
        # Start bot
        logger.info("Bot is running...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def send_notification(message: str, parse_mode: str = 'Markdown'):
    """Send notification to admin"""
    if not ADMIN_CHAT_ID:
        logger.warning("No admin chat ID configured")
        return
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': parse_mode
        }
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please configure your bot token in telegram-config.json")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Copy the token to telegram-config.json")
        sys.exit(1)
    
    bot = OpenClawBot()
    
    # Send startup notification
    send_notification(
        f"🚀 **OpenClaw Bot Started**\n\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Admin: {ADMIN_PHONE}"
    )
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        send_notification("🛑 **OpenClaw Bot Stopped**")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        send_notification(f"❌ **Bot Error:**\n{str(e)}")
