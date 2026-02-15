"""
Money Tracker Module - Financial tracking.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class MoneyTracker:
    """Money tracking functionality."""
    
    def __init__(self):
        pass
    
    async def show_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show financial dashboard."""
        message = (
            "💰 *Financial Dashboard*\n\n"
            "📊 *This Month:*\n"
            "• Target: €5,363\n"
            "• Log your income to see progress\n\n"
            "*Commands:*\n"
            "• /income - Log income entry\n\n"
            "_Feature in development..._"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def log_income_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start income logging flow."""
        await update.message.reply_text(
            "💰 *Log Income*\n\n"
            "Format: Category | Gross | Bills | Description\n"
            "Example: `personal | 2000 | 800 | VA disability`\n\n"
            "Categories: personal, blokblok",
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle money callbacks."""
        pass
