"""
AgentBear News - Daily AI News Site
Database models for articles and content
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "news.db"

class NewsDatabase:
    """Manages news articles and content"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                subtitle TEXT,
                content TEXT NOT NULL,
                summary TEXT,
                source_url TEXT,
                source_name TEXT,
                category TEXT,
                tags TEXT,  -- JSON array
                featured BOOLEAN DEFAULT 0,
                views INTEGER DEFAULT 0,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#6366f1'
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('ai-research', 'AI Research', 'Latest breakthroughs and papers', '#8b5cf6'),
            ('industry', 'Industry', 'Big tech moves and startups', '#3b82f6'),
            ('policy', 'Policy', 'Regulation and governance', '#10b981'),
            ('infra', 'Infrastructure', 'AI infra, compute, and hardware', '#f59e0b'),
            ('agents', 'Agents', 'AI agents and automation', '#ec4899'),
        ]
        
        for slug, name, desc, color in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (slug, name, description, color)
                VALUES (?, ?, ?, ?)
            ''', (slug, name, desc, color))
        
        conn.commit()
        conn.close()
    
    def create_article(self, data: dict) -> int:
        """Create a new article"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO articles 
            (slug, title, subtitle, content, summary, source_url, source_name, 
             category, tags, featured, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('slug'),
            data.get('title'),
            data.get('subtitle'),
            data.get('content'),
            data.get('summary'),
            data.get('source_url'),
            data.get('source_name'),
            data.get('category', 'industry'),
            json.dumps(data.get('tags', [])),
            data.get('featured', False),
            data.get('published_at', datetime.now().isoformat())
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id
    
    def get_article(self, slug: str) -> dict:
        """Get article by slug"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles WHERE slug = ?
        ''', (slug,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row, cursor)
        return None
    
    def get_article_by_id(self, article_id: int) -> dict:
        """Get article by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles WHERE id = ?
        ''', (article_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row, cursor)
        return None
    
    def get_articles(self, category=None, featured=None, limit=20, offset=0) -> list:
        """Get articles with filters"""
        conn = sqlite3.connect(self.db_path)
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
        
        return [self._row_to_dict(row, cursor) for row in rows]
    
    def get_featured_article(self) -> dict:
        """Get today's featured article"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            WHERE featured = 1 
            ORDER BY published_at DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row, cursor)
        return None
    
    def get_categories(self) -> list:
        """Get all categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM categories ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'slug': row[1],
                'name': row[2],
                'description': row[3],
                'color': row[4]
            }
            for row in rows
        ]
    
    def increment_views(self, slug: str):
        """Increment article view count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE articles SET views = views + 1 WHERE slug = ?
        ''', (slug,))
        
        conn.commit()
        conn.close()
    
    def _row_to_dict(self, row, cursor) -> dict:
        """Convert DB row to dict"""
        columns = [description[0] for description in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse JSON fields
        if result.get('tags'):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        
        return result
    
    def get_stats(self) -> dict:
        """Get site stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(views) FROM articles')
        total_views = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM articles 
            GROUP BY category
        ''')
        categories = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'total_views': total_views,
            'categories': categories
        }
