"""
AgentBear Corps - Daily AI News Site
Flask application for serving news content - Vercel compatible
"""

import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'agentbear-news-dev-key')

# Database path - use /tmp for writable operations in serverless
def get_db_path():
    """Get database path compatible with Vercel serverless"""
    # In Vercel, use /tmp for any writes
    if os.environ.get('VERCEL'):
        return '/tmp/news.db'
    # Local development - use repo directory
    return os.path.join(os.path.dirname(__file__), 'news.db')

DB_PATH = get_db_path()

def get_db_connection():
    """Get database connection with proper settings"""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

# Copy DB to /tmp on Vercel if needed
def init_db():
    """Initialize database for Vercel"""
    if os.environ.get('VERCEL'):
        import shutil
        src = os.path.join(os.path.dirname(__file__), 'news.db')
        dst = '/tmp/news.db'
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy(src, dst)
                print(f"Copied DB to {dst}")
            except Exception as e:
                print(f"DB Copy Error: {e}")

# Initialize on startup
init_db()

# Categories data (static)
CATEGORIES = [
    {'slug': 'ai-research', 'name': 'AI Research', 'description': 'Latest breakthroughs and papers', 'color': '#8b5cf6'},
    {'slug': 'industry', 'name': 'Industry', 'description': 'Big tech moves and startups', 'color': '#3b82f6'},
    {'slug': 'policy', 'name': 'Policy', 'description': 'Regulation and governance', 'color': '#10b981'},
    {'slug': 'infra', 'name': 'Infrastructure', 'description': 'AI infra, compute, and hardware', 'color': '#f59e0b'},
    {'slug': 'agents', 'name': 'Agents', 'description': 'AI agents and automation', 'color': '#ec4899'},
]

def get_articles(category=None, featured=None, limit=20, offset=0):
    """Get articles from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    query = 'SELECT * FROM articles WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if featured is not None:
        query += ' AND featured = ?'
        params.append(1 if featured else 0)
    
    query += ' ORDER BY published_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Query Error: {e}")
        return []

def get_article(slug):
    """Get single article by slug"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM articles WHERE slug = ?', (slug,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Article Query Error: {e}")
        return None

def get_featured_article():
    """Get featured article"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM articles WHERE featured = 1 ORDER BY published_at DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Featured Query Error: {e}")
        return None

@app.context_processor
def inject_globals():
    """Inject global template variables"""
    return {
        'site_name': 'AgentBear Corps',
        'site_tagline': 'A Beary Cute News Agency Reporting on AI',
        'current_year': datetime.now().year,
        'categories': CATEGORIES
    }

@app.route('/')
def index():
    """Homepage with featured article and recent posts"""
    featured = get_featured_article()
    recent = get_articles(limit=6)
    
    # Remove featured from recent if present
    if featured:
        recent = [a for a in recent if a['slug'] != featured['slug']][:5]
    
    return render_template('news_index.html', 
                         featured=featured, 
                         recent=recent)

@app.route('/article/<slug>')
def article(slug):
    """Individual article page"""
    article = get_article(slug)
    if not article:
        abort(404)
    
    # Get related articles
    related = get_articles(category=article['category'], limit=3)
    related = [a for a in related if a['slug'] != slug]
    
    return render_template('news_article.html', 
                         article=article, 
                         related=related)

@app.route('/category/<slug>')
def category(slug):
    """Category page"""
    category_info = next((c for c in CATEGORIES if c['slug'] == slug), None)
    
    if not category_info:
        abort(404)
    
    articles = get_articles(category=slug, limit=20)
    
    return render_template('news_category.html',
                         category=category_info,
                         articles=articles)

@app.route('/archive')
def archive():
    """Archive page with all articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    articles = get_articles(limit=per_page, offset=(page-1)*per_page)
    
    return render_template('news_archive.html',
                         articles=articles,
                         page=page)

@app.route('/about')
def about():
    """About page"""
    return render_template('news_about.html')

@app.route('/subscribe')
def subscribe():
    """Subscribe page"""
    return render_template('news_subscribe.html')

# API routes
@app.route('/api/articles')
def api_articles():
    """API endpoint for articles"""
    category = request.args.get('category')
    limit = request.args.get('limit', 20, type=int)
    
    articles = get_articles(category=category, limit=limit)
    return jsonify({'articles': articles})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
