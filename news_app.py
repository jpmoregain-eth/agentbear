"""
AgentBear News - Daily AI News Site
Flask application for serving news content
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort
from news_database import NewsDatabase

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'agentbear-news-dev-key')

# Initialize database
db = NewsDatabase()

@app.context_processor
def inject_globals():
    """Inject global template variables"""
    return {
        'site_name': 'AgentBear Corps',
        'site_tagline': 'A Beary Cute News Agency Reporting on AI',
        'current_year': datetime.now().year,
        'categories': db.get_categories()
    }

@app.route('/')
def index():
    """Homepage with featured article and recent posts"""
    featured = db.get_featured_article()
    recent = db.get_articles(limit=6)
    
    # Remove featured from recent if present
    if featured:
        recent = [a for a in recent if a['slug'] != featured['slug']][:5]
    
    return render_template('news_index.html', 
                         featured=featured, 
                         recent=recent)

@app.route('/article/<slug>')
def article(slug):
    """Individual article page"""
    article = db.get_article(slug)
    if not article:
        abort(404)
    
    # Increment views
    db.increment_views(slug)
    
    # Get related articles
    related = db.get_articles(
        category=article['category'], 
        limit=3
    )
    related = [a for a in related if a['slug'] != slug]
    
    return render_template('news_article.html', 
                         article=article, 
                         related=related)

@app.route('/category/<slug>')
def category(slug):
    """Category page"""
    categories = db.get_categories()
    category_info = next((c for c in categories if c['slug'] == slug), None)
    
    if not category_info:
        abort(404)
    
    articles = db.get_articles(category=slug, limit=20)
    
    return render_template('news_category.html',
                         category=category_info,
                         articles=articles)

@app.route('/archive')
def archive():
    """Archive page with all articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    articles = db.get_articles(limit=per_page, offset=(page-1)*per_page)
    stats = db.get_stats()
    
    return render_template('news_archive.html',
                         articles=articles,
                         page=page,
                         stats=stats)

@app.route('/about')
def about():
    """About page"""
    return render_template('news_about.html')

# Admin routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    stats = db.get_stats()
    recent = db.get_articles(limit=10)
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent=recent)

@app.route('/admin/article/new', methods=['GET', 'POST'])
def admin_create_article():
    """Create new article"""
    if request.method == 'POST':
        data = {
            'slug': request.form.get('slug'),
            'title': request.form.get('title'),
            'subtitle': request.form.get('subtitle'),
            'content': request.form.get('content'),
            'summary': request.form.get('summary'),
            'source_url': request.form.get('source_url'),
            'source_name': request.form.get('source_name'),
            'category': request.form.get('category'),
            'tags': request.form.get('tags', '').split(','),
            'featured': request.form.get('featured') == 'on',
            'published_at': datetime.now().isoformat()
        }
        
        article_id = db.create_article(data)
        return jsonify({'success': True, 'id': article_id, 'slug': data['slug']})
    
    categories = db.get_categories()
    return render_template('admin_create.html', categories=categories)

# API routes
@app.route('/api/articles')
def api_articles():
    """API endpoint for articles"""
    category = request.args.get('category')
    limit = request.args.get('limit', 20, type=int)
    
    articles = db.get_articles(category=category, limit=limit)
    return jsonify({'articles': articles})

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    return jsonify(db.get_stats())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
