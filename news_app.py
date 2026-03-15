"""
AgentBear Corps - Daily AI News Site
Read-only Flask app for Vercel serverless
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)

# Database path - read from repo (read-only, no writes)
DB_PATH = os.path.join(os.path.dirname(__file__), 'news.db')

# Static categories
CATEGORIES = [
    {'slug': 'ai-research', 'name': 'AI Research', 'description': 'Latest breakthroughs and papers', 'color': '#8b5cf6'},
    {'slug': 'industry', 'name': 'Industry', 'description': 'Big tech moves and startups', 'color': '#3b82f6'},
    {'slug': 'policy', 'name': 'Policy', 'description': 'Regulation and governance', 'color': '#10b981'},
    {'slug': 'infra', 'name': 'Infrastructure', 'description': 'AI infra, compute, and hardware', 'color': '#f59e0b'},
    {'slug': 'agents', 'name': 'Agents', 'description': 'AI agents and automation', 'color': '#ec4899'},
]

def get_db():
    """Get read-only DB connection"""
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_articles(category=None, featured=None, limit=20, offset=0):
    """Get articles (read-only)"""
    conn = get_db()
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
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_article(slug):
    """Get single article"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_featured_article():
    """Get featured article"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE featured = 1 ORDER BY published_at DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

@app.context_processor
def inject_globals():
    return {
        'site_name': 'AgentBear Corps',
        'site_tagline': 'A Beary Cute News Agency Reporting on AI',
        'current_year': datetime.now().year,
        'categories': CATEGORIES
    }

@app.route('/')
def index():
    # Get all articles sorted by date (newest first)
    all_articles = get_articles(limit=20)
    
    # Fresh from the Honeypot: 4 most recent (for 2x2 grid on desktop)
    fresh = all_articles[:4]
    
    # Latest from the Field: next 4 most recent (5th, 6th, 7th, 8th)
    latest = all_articles[4:8]
    
    return render_template('news_index.html', fresh=fresh, latest=latest)

@app.route('/article/<slug>')
def article(slug):
    article = get_article(slug)
    if not article:
        abort(404)
    related = get_articles(category=article['category'], limit=3)
    related = [a for a in related if a['slug'] != slug]
    return render_template('news_article.html', article=article, related=related)

@app.route('/category/<slug>')
def category(slug):
    category_info = next((c for c in CATEGORIES if c['slug'] == slug), None)
    if not category_info:
        abort(404)
    articles = get_articles(category=slug, limit=20)
    return render_template('news_category.html', category=category_info, articles=articles)

@app.route('/archive')
def archive():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # Skip first 8 articles (shown on homepage: 4 in Honeypot + 4 in Latest)
    offset = 8 + ((page-1) * per_page)
    articles = get_articles(limit=per_page, offset=offset)
    return render_template('news_archive.html', articles=articles, page=page)

@app.route('/about')
def about():
    return render_template('news_about.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/api/articles')
def api_articles():
    category = request.args.get('category')
    limit = request.args.get('limit', 20, type=int)
    articles = get_articles(category=category, limit=limit)
    return jsonify({'articles': articles})
