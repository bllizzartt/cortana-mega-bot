"""Meal Bot - Recipe suggestions."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
from modules.meal_data import ALL_RECIPES, CATEGORIES

class MealBot:
    def __init__(self):
        self.recipes = ALL_RECIPES
        self.categories = CATEGORIES
    
    async def suggest_dinner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        recipe = random.choice(self.recipes)
        ingredients = "\n".join([f"• {i}" for i in recipe['ingredients'][:5]])
        message = (
            f"🍽️ *{recipe['name']}* ({recipe['cuisine']})\n"
            f"⏱️ {recipe['time']} min | 💰 €{recipe['cost']}\n\n"
            f"_{recipe['description']}_\n\n"
            f"*Ingredients:*\n{ingredients}..."
        )
        keyboard = [[InlineKeyboardButton("🔄 Another", callback_data="meal:next")]]
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query.data == "meal:next":
            await self.suggest_dinner(update, context)
