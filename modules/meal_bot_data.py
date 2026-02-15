"""
Meal Bot Module - Wrapper for recipe data.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random

from .meal_bot_data import ALL_RECIPES, CATEGORIES


class MealBot:
    """Meal suggestion bot functionality."""
    
    def __init__(self):
        self.recipes = ALL_RECIPES
        self.categories = CATEGORIES
    
    async def suggest_dinner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Suggest a random dinner recipe."""
        recipe = random.choice(self.recipes)
        
        ingredients = "\n".join([f"• {i}" for i in recipe['ingredients'][:8]])
        
        message = (
            f"🍽️ *{recipe['name']}*\n"
            f"⏱️ {recipe.get('time', '30')} min | 💰 €{recipe.get('cost', 8)}\n\n"
            f"{recipe.get('description', 'Delicious home-cooked meal')}\n\n"
            f"*Ingredients:*\n{ingredients}\n..."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Another", callback_data="meal:next"),
                InlineKeyboardButton("📖 Recipe", callback_data=f"meal:recipe:{recipe['name']}"),
            ]
        ]
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle meal callbacks."""
        query = update.callback_query
        data = query.data
        
        if data == "meal:next":
            await self.suggest_dinner(update, context)
