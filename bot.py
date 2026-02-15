#!/usr/bin/env python3
"""Cortana Mega Bot - All features in one bot."""

import os
import sys
import logging
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, ConversationHandler, filters
)

# Import modules
from modules.video_gen import VideoGenerator as VideoGen
from modules.meal_bot import MealBot
from modules.money_tracker import MoneyTracker
from modules.lead_scraper import LeadScraper

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8572628843:AAFFl71Dpj3DRyAYJrCRJ66sYBGKJV3y9PA')
ADMIN_ID = int(os.getenv('ADMIN_ID', '8148840480'))

class MegaBot:
    """Unified bot with all features."""
    
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.video = VideoGen()
        self.meal = MealBot()
        self.money = MoneyTracker()
        self.leads = LeadScraper()
        self.setup_handlers()
    
    def setup_handlers(self):
        # Main commands
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        
        # Video generation
        self.app.add_handler(CommandHandler("video", self.video_cmd))
        
        # Meal bot
        self.app.add_handler(CommandHandler("dinner", self.dinner_cmd))
        self.app.add_handler(CommandHandler("meal", self.dinner_cmd))
        
        # Money tracker
        self.app.add_handler(CommandHandler("money", self.money_cmd))
        self.app.add_handler(CommandHandler("income", self.income_cmd))
        
        # Lead scraper
        self.app.add_handler(CommandHandler("leads", self.leads_cmd))
        
        # Berman strategies
        self.app.add_handler(CommandHandler("memory", self.memory_cmd))
        self.app.add_handler(CommandHandler("calendar", self.calendar_cmd))
        self.app.add_handler(CommandHandler("trade", self.trade_cmd))
        
        # Callbacks
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Errors
        self.app.add_error_handler(self.handle_error)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message."""
        welcome = (
            "⚡ *Cortana Mega Bot*\n\n"
            "Your personal AI assistant. Choose a feature:\n\n"
            "🎥 */video* - AI video generation\n"
            "🍳 */dinner* - Dinner suggestions\n"
            "💰 */money* - Track income & wealth\n"
            "📊 */leads* - Lead generation\n"
            "🧠 */memory* - Berman memory system\n"
            "📅 */calendar* - Smart scheduling\n"
            "📈 */trade* - Polymarket bot\n\n"
            "Type /help for all commands."
        )
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help message."""
        help_text = (
            "⚡ *Cortana Commands*\n\n"
            "🎥 *Video Generation*\n"
            "• /video - AI video generation\n\n"
            "🍳 *Meal Bot*\n"
            "• /dinner - Dinner suggestions\n\n"
            "💰 *Money Tracker*\n"
            "• /money - Financial status\n"
            "• /income - Log income\n\n"
            "📊 *Lead Generation*\n"
            "• /leads - Find leads\n\n"
            "🧠 *Berman Strategies*\n"
            "• /memory - Memory management\n"
            "• /calendar - Smart scheduling\n"
            "• /trade - Polymarket bot\n\n"
            "⚡ @cortana_support"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def video_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start video generation."""
        await self.video.start_generation(update, context)
    
    async def dinner_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get dinner suggestion."""
        await self.meal.suggest_dinner(update, context)
    
    async def money_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show financial dashboard."""
        await self.money.show_dashboard(update, context)
    
    async def income_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log income."""
        await self.money.log_income_start(update, context)
    
    async def leads_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start lead scraping."""
        await self.leads.start_scrape(update, context)
    
    async def memory_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Memory management."""
        message = (
            "🧠 *Memory Management*\n\n"
            "Berman Strategy: Long-term memory storage\n\n"
            "*Features:*\n"
            "• Weekly compression: Auto-summarize old memories\n"
            "• Key facts extraction: Important info never lost\n"
            "• Semantic search: Find anything instantly\n\n"
            "*Status:* ✅ Active\n"
            "Daily maintenance at 3 AM"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def calendar_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Calendar automation."""
        message = (
            "📅 *Calendar & Email Automation*\n\n"
            "Berman Strategy: Integration = Power\n\n"
            "*Features:*\n"
            "• Smart scheduling: High energy = hard tasks\n"
            "• Auto-decline: Conflicting invites\n"
            "• Email triage: Urgent/important/bulk auto-sort\n\n"
            "*Status:* 🔄 In development\n"
            "Connect Google Calendar to activate"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def trade_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Polymarket trading."""
        message = (
            "📈 *Polymarket Trading Bot*\n\n"
            "Berman Strategy: AI-powered prediction markets\n\n"
            "*Safety Limits:*\n"
            "• Max 5% per trade\n"
            "• Daily loss limit: €50\n"
            "• Manual approval >€100\n\n"
            "*Status:* 🔄 API integration pending\n"
            "Risk management active"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks."""
        query = update.callback_query
        await query.answer()
        
        # Route to appropriate module
        data = query.data
        if data.startswith('video:'):
            await self.video.handle_callback(update, context)
        elif data.startswith('meal:'):
            await self.meal.handle_callback(update, context)
        elif data.startswith('money:'):
            await self.money.handle_callback(update, context)
        elif data.startswith('lead:'):
            await self.leads.handle_callback(update, context)
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f'Error: {context.error}')
        if update and update.effective_message:
            await update.effective_message.reply_text(
                '⚠️ Something went wrong. Try again or type /help'
            )
    
    def run(self):
        """Start the bot."""
        logger.info('Starting Mega Bot...')
        self.app.run_polling()

if __name__ == '__main__':
    bot = MegaBot()
    bot.run()
