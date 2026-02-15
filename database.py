"""
Unified Database for Cortana Mega Bot.
Handles all data: video jobs, meals, money, and leads.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any


DATABASE_PATH = Path("./mega_bot.db")


@contextmanager
def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize all database tables."""
    with get_db() as db:
        # Video generation jobs table
        db.execute("""
            CREATE TABLE IF NOT EXISTS video_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                prompt TEXT,
                photos_json TEXT,
                video_path TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User sessions for video generation
        db.execute("""
            CREATE TABLE IF NOT EXISTS video_sessions (
                user_id INTEGER PRIMARY KEY,
                photos_json TEXT,
                prompt TEXT,
                state TEXT DEFAULT 'idle',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Recipes table
        db.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                cuisine TEXT,
                ingredients TEXT,
                instructions TEXT,
                prep_time INTEGER,
                cook_time INTEGER,
                servings INTEGER,
                difficulty TEXT,
                is_favorite INTEGER DEFAULT 0
            )
        """)

        # Meal history (cooked meals)
        db.execute("""
            CREATE TABLE IF NOT EXISTS meal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_id INTEGER,
                recipe_name TEXT,
                cooked_date TEXT,
                notes TEXT,
                rating INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Income categories
        db.execute("""
            CREATE TABLE IF NOT EXISTS income_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category_type TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Income sources
        db.execute("""
            CREATE TABLE IF NOT EXISTS income_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES income_categories(id)
            )
        """)

        # Income entries
        db.execute("""
            CREATE TABLE IF NOT EXISTS income_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT,
                source_name TEXT,
                gross_amount REAL,
                net_amount REAL,
                bills_amount REAL,
                entry_date TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Debts table
        db.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                principal REAL,
                current_balance REAL,
                interest_rate REAL,
                minimum_payment REAL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Debt payments
        db.execute("""
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER,
                amount REAL,
                payment_date TEXT,
                FOREIGN KEY (debt_id) REFERENCES debts(id)
            )
        """)

        # Assets table
        db.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                asset_type TEXT,
                current_value REAL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Wealth goals
        db.execute("""
            CREATE TABLE IF NOT EXISTS wealth_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL,
                goal_type TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Leads table
        db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                company TEXT,
                title TEXT,
                linkedin_url TEXT,
                status TEXT DEFAULT 'new',
                source TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.commit()

        # Seed default income categories if empty
        cur = db.execute("SELECT COUNT(*) FROM income_categories")
        if cur.fetchone()[0] == 0:
            seed_income_categories(db)

        # Seed recipes if empty
        cur = db.execute("SELECT COUNT(*) FROM recipes")
        if cur.fetchone()[0] == 0:
            seed_recipes(db)


def seed_income_categories(db):
    """Seed default income categories."""
    categories = [
        ("VA Income", "personal"),
        ("Rental Income", "personal"),
        ("Education/School", "personal"),
        ("Blok Blok Business", "business"),
        ("Other Personal", "personal"),
        ("Other Business", "business"),
    ]
    db.executemany(
        "INSERT INTO income_categories (name, category_type) VALUES (?, ?)",
        categories
    )


def seed_recipes(db):
    """Seed recipes from the recipes module."""
    from modules.meal_bot import ALL_RECIPES
    for recipe in ALL_RECIPES:
        db.execute("""
            INSERT INTO recipes (name, category, cuisine, ingredients, instructions, prep_time, cook_time, servings, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe.get("name"),
            recipe.get("category"),
            recipe.get("cuisine"),
            json.dumps(recipe.get("ingredients", [])),
            json.dumps(recipe.get("instructions", [])),
            recipe.get("prep_time", 0),
            recipe.get("cook_time", 0),
            recipe.get("servings", 2),
            recipe.get("difficulty", "Medium")
        ))


# ============== VIDEO JOB FUNCTIONS ==============

def create_video_job(user_id: int, job_id: str, prompt: str, photos: List[str]) -> int:
    """Create a new video generation job."""
    with get_db() as db:
        result = db.execute("""
            INSERT INTO video_jobs (user_id, job_id, prompt, photos_json, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (user_id, job_id, prompt, json.dumps(photos)))
        db.commit()
        return result.lastrowid


def update_video_job(job_id: str, status: str = None, video_path: str = None, error_message: str = None):
    """Update video job status."""
    with get_db() as db:
        if status:
            db.execute("UPDATE video_jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                      (status, datetime.now().isoformat(), job_id))
        if video_path:
            db.execute("UPDATE video_jobs SET video_path = ? WHERE job_id = ?", (video_path, job_id))
        if error_message:
            db.execute("UPDATE video_jobs SET error_message = ? WHERE job_id = ?", (error_message, job_id))
        db.commit()


def get_video_job(job_id: str) -> Optional[Dict]:
    """Get video job by job_id."""
    with get_db() as db:
        result = db.execute("SELECT * FROM video_jobs WHERE job_id = ?", (job_id,)).fetchone()
        return dict(result) if result else None


def get_user_video_jobs(user_id: int, limit: int = 10) -> List[Dict]:
    """Get recent video jobs for a user."""
    with get_db() as db:
        results = db.execute(
            "SELECT * FROM video_jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in results]


# ============== VIDEO SESSION FUNCTIONS ==============

def set_user_session(user_id: int, state: str, photos: List[str] = None, prompt: str = None):
    """Set or update user video session."""
    with get_db() as db:
        db.execute("""
            INSERT OR REPLACE INTO video_sessions (user_id, state, photos_json, prompt)
            VALUES (?, ?, ?, ?)
        """, (user_id, state, json.dumps(photos or []), prompt))
        db.commit()


def get_user_session(user_id: int) -> Optional[Dict]:
    """Get user video session."""
    with get_db() as db:
        result = db.execute("SELECT * FROM video_sessions WHERE user_id = ?", (user_id,)).fetchone()
        return dict(result) if result else None


def clear_user_session(user_id: int):
    """Clear user video session."""
    with get_db() as db:
        db.execute("DELETE FROM video_sessions WHERE user_id = ?", (user_id,))
        db.commit()


# ============== MEAL FUNCTIONS ==============

def get_recipe(recipe_id: int) -> Optional[Dict]:
    """Get recipe by ID."""
    with get_db() as db:
        result = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        return dict(result) if result else None


def get_random_recipe(category: str = None) -> Optional[Dict]:
    """Get random recipe, optionally filtered by category."""
    with get_db() as db:
        if category:
            result = db.execute(
                "SELECT * FROM recipes WHERE category = ? ORDER BY RANDOM() LIMIT 1",
                (category,)
            ).fetchone()
        else:
            result = db.execute("SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1").fetchone()
        return dict(result) if result else None


def get_all_recipes() -> List[Dict]:
    """Get all recipes."""
    with get_db() as db:
        results = db.execute("SELECT * FROM recipes").fetchall()
        return [dict(r) for r in results]


def search_recipes(query: str) -> List[Dict]:
    """Search recipes by name or ingredients."""
    with get_db() as db:
        results = db.execute(
            "SELECT * FROM recipes WHERE name LIKE ? OR ingredients LIKE ?",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
        return [dict(r) for r in results]


def log_cooked_meal(user_id: int, recipe_id: int, recipe_name: str, rating: int = None, notes: str = None):
    """Log a cooked meal."""
    with get_db() as db:
        db.execute("""
            INSERT INTO meal_history (user_id, recipe_id, recipe_name, cooked_date, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, recipe_id, recipe_name, datetime.now().strftime("%Y-%m-%d"), rating, notes))
        db.commit()


def get_meal_history(user_id: int, limit: int = 20) -> List[Dict]:
    """Get meal cooking history."""
    with get_db() as db:
        results = db.execute(
            "SELECT * FROM meal_history WHERE user_id = ? ORDER BY cooked_date DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in results]


# ============== MONEY FUNCTIONS ==============

def get_income_categories() -> List[Dict]:
    """Get all income categories."""
    with get_db() as db:
        results = db.execute("SELECT * FROM income_categories WHERE is_active = 1").fetchall()
        return [dict(r) for r in results]


def get_sources_for_category(category_id: int) -> List[Dict]:
    """Get sources for a category."""
    with get_db() as db:
        results = db.execute("SELECT * FROM income_sources WHERE category_id = ?", (category_id,)).fetchall()
        return [dict(r) for r in results]


def log_income(category_name: str, gross_amount: float, net_amount: float = None,
               bills_amount: float = 0, entry_date: str = None, description: str = ""):
    """Log income entry."""
    with get_db() as db:
        db.execute("""
            INSERT INTO income_entries (category_name, gross_amount, net_amount, bills_amount, entry_date, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category_name, gross_amount, net_amount or gross_amount, bills_amount,
              entry_date or datetime.now().strftime("%Y-%m-%d"), description))
        db.commit()


def get_income_summary(month: int = None, year: int = None) -> Dict:
    """Get income summary for a month."""
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year

    with get_db() as db:
        results = db.execute("""
            SELECT category_name, SUM(gross_amount) as total_gross, SUM(net_amount) as total_net,
                   SUM(bills_amount) as total_bills, COUNT(*) as count
            FROM income_entries
            WHERE strftime('%m', entry_date) = ? AND strftime('%Y', entry_date) = ?
            GROUP BY category_name
        """, (f"{month:02d}", str(year))).fetchall()

        personal = sum(r['total_gross'] for r in results if get_category_type(r['category_name']) == 'personal')
        business = sum(r['total_gross'] for r in results if get_category_type(r['category_name']) == 'business')

        return {
            'by_category': [dict(r) for r in results],
            'total_gross': sum(r['total_gross'] for r in results),
            'total_net': sum(r['total_net'] for r in results),
            'total_bills': sum(r['total_bills'] for r in results),
            'personal_income': personal,
            'business_income': business,
            'month': month,
            'year': year
        }


def get_category_type(category_name: str) -> str:
    """Get category type (personal/business)."""
    with get_db() as db:
        result = db.execute(
            "SELECT category_type FROM income_categories WHERE name = ?",
            (category_name,)
        ).fetchone()
        return result['category_type'] if result else 'personal'


def get_all_debts() -> List[Dict]:
    """Get all active debts."""
    with get_db() as db:
        results = db.execute("SELECT * FROM debts WHERE is_active = 1").fetchall()
        return [dict(r) for r in results]


def add_debt(name: str, principal: float, interest_rate: float, minimum_payment: float):
    """Add a new debt."""
    with get_db() as db:
        db.execute("""
            INSERT INTO debts (name, principal, current_balance, interest_rate, minimum_payment)
            VALUES (?, ?, ?, ?, ?)
        """, (name, principal, principal, interest_rate, minimum_payment))
        db.commit()


def get_net_worth() -> Dict:
    """Calculate net worth."""
    with get_db() as db:
        assets = db.execute("SELECT SUM(current_value) as total FROM assets WHERE is_active = 1").fetchone()
        debts = db.execute("SELECT SUM(current_balance) as total FROM debts WHERE is_active = 1").fetchone()

        total_assets = assets['total'] or 0
        total_debts = debts['total'] or 0
        net_worth = total_assets - total_debts

        debt_ratio = (total_debts / total_assets * 100) if total_assets > 0 else 0

        return {
            'total_assets': total_assets,
            'total_debts': total_debts,
            'net_worth': net_worth,
            'debt_to_asset_ratio': debt_ratio
        }


def get_wealth_goals() -> List[Dict]:
    """Get all wealth goals."""
    with get_db() as db:
        results = db.execute("SELECT * FROM wealth_goals").fetchall()
        return [dict(r) for r in results]


def add_wealth_goal(name: str, target_amount: float, goal_type: str):
    """Add a wealth goal."""
    with get_db() as db:
        db.execute("INSERT INTO wealth_goals (name, target_amount, goal_type) VALUES (?, ?, ?)",
                  (name, target_amount, goal_type))
        db.commit()


# ============== LEAD FUNCTIONS ==============

def add_lead(name: str = None, email: str = None, company: str = None,
             title: str = None, linkedin_url: str = None, source: str = "manual", notes: str = None):
    """Add a new lead."""
    with get_db() as db:
        db.execute("""
            INSERT INTO leads (name, email, company, title, linkedin_url, source, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, company, title, linkedin_url, source, notes))
        db.commit()


def get_leads(status: str = None, limit: int = 50) -> List[Dict]:
    """Get leads, optionally filtered by status."""
    with get_db() as db:
        if status:
            results = db.execute(
                "SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            results = db.execute(
                "SELECT * FROM leads ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [dict(r) for r in results]


def update_lead_status(lead_id: int, status: str):
    """Update lead status."""
    with get_db() as db:
        db.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
        db.commit()


def export_leads_csv() -> str:
    """Export leads to CSV format."""
    leads = get_leads()
    if not leads:
        return ""

    lines = ["Name,Email,Company,Title,LinkedIn,Status,Source,Notes"]
    for lead in leads:
        lines.append(f"{lead.get('name','')},{lead.get('email','')},{lead.get('company','')},"
                    f"{lead.get('title','')},{lead.get('linkedin_url','')},"
                    f"{lead.get('status','')},{lead.get('source','')},{lead.get('notes','')}")
    return "\n".join(lines)
