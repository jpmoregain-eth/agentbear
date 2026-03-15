# Simple init script for Vercel
import os
import sys

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_database import NewsDatabase
from create_terafab_article import create_terafab_article

# Initialize DB
db_path = os.environ.get('DATABASE_PATH', 'news.db')
db = NewsDatabase(db_path)

# Check if articles exist
stats = db.get_stats()
if stats['total_articles'] == 0:
    print("No articles found, creating sample data...")
    create_terafab_article()
    print("Sample data created!")
else:
    print(f"Database ready with {stats['total_articles']} articles")
