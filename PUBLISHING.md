# AgentBear Corps - Publishing Guide

## How to Add New Articles

This guide documents the process for publishing new articles to the AgentBear Corps news site.

---

## Quick Workflow

1. **Find trending AI story**
2. **Write article** (2,000-4,000 words with hot takes)
3. **Add to database** using Python script
4. **Mark as featured** (optional - for daily lead story)
5. **Commit and push** to GitHub
6. **Vercel auto-deploys** (within 1-2 minutes)

---

## Step-by-Step Process

### Step 1: SSH into Server

```bash
ssh user@your-server
```

### Step 2: Navigate to Project

```bash
cd ~/Documents/agentbearcorps
source venv/bin/activate
```

### Step 3: Create Article Script

Create a new file `add_article.py`:

```python
#!/usr/bin/env python3
"""Add new article to AgentBear Corps"""

from news_database import NewsDatabase
from datetime import datetime

db = NewsDatabase('news.db')

article = {
    'slug': 'your-article-slug-here',
    'title': 'Your Article Title',
    'subtitle': 'Compelling subtitle that hooks readers',
    'content': '''
<p>Opening paragraph with hook...</p>

<h2>Section Heading</h2>
<p>Your content here...</p>

<h2>Another Section</h2>
<p>More content...</p>

<blockquote>
Important quote or insight
</blockquote>

<h2>Hot Take</h2>
<p>Your controversial opinion here...</p>
    ''',
    'summary': 'One sentence summary for cards and previews',
    'source_url': 'https://original-source.com/article',
    'source_name': 'Source Name',
    'category': 'industry',  # Options: industry, agents, infra, policy, research
    'tags': ['tag1', 'tag2', 'tag3'],
    'featured': False,  # Set True for daily lead story
    'published_at': datetime.now().isoformat()
}

try:
    article_id = db.create_article(article)
    print(f"✅ Article created: {article['title']}")
    print(f"   ID: {article_id}")
    print(f"   Slug: {article['slug']}")
    print(f"   URL: https://agentbearcorps.com/article/{article['slug']}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Step 4: Run the Script

```bash
python3 add_article.py
```

### Step 5: Verify Article Added

```bash
# Check database
sqlite3 news.db "SELECT title FROM articles ORDER BY id DESC LIMIT 3;"
```

### Step 6: Git Commit & Push

```bash
git add news.db
git commit -m "Add new article: [Article Title]"
git push origin main
```

### Step 7: Verify Live Site

Wait 1-2 minutes, then check:
- https://agentbearcorps.com
- https://agentbearcorps.com/article/your-article-slug

---

## Article Categories

| Category | Use For |
|----------|---------|
| `industry` | Big tech moves, startups, business news |
| `agents` | AI agents, automation, orchestration |
| `infra` | Hardware, compute, data centers, chips |
| `policy` | Regulation, governance, ethics |
| `research` | Papers, breakthroughs, lab announcements |

---

## Article Structure Template

```html
<p>Hook paragraph - why this matters now...</p>

<h2>What Happened</h2>
<p>Facts and details...</p>

<h2>The Technical Details</h2>
<p>Deep dive for tech readers...</p>
<ul>
    <li>Bullet point 1</li>
    <li>Bullet point 2</li>
</ul>

<h2>Industry Impact</h2>
<p>Analysis of implications...</p>

<h2>🔥 Our Hot Take</h2>
<p><strong>Bold opinion here...</strong></p>
<p>Your unfiltered analysis...</p>

<h2>What to Watch</h2>
<p>Next steps or predictions...</p>
```

---

## Making an Article Featured (Daily Lead)

To set an article as the featured daily story:

```python
# In add_article.py, set:
'featured': True

# Or update existing article:
import sqlite3
conn = sqlite3.connect('news.db')
cursor = conn.cursor()
cursor.execute("UPDATE articles SET featured = 1 WHERE slug = 'your-slug'")
conn.commit()
conn.close()
```

**Note:** Only ONE article should be featured at a time. Unset previous featured article first:

```python
cursor.execute("UPDATE articles SET featured = 0 WHERE featured = 1")
```

---

## Troubleshooting

### Article not showing on site
1. Check if `git push` succeeded
2. Verify Vercel deployment: https://vercel.com/dashboard
3. Check article exists: `sqlite3 news.db "SELECT * FROM articles WHERE slug='your-slug'"`

### Database locked error
```bash
# Kill any Python processes using the DB
pkill -f python3
# Retry
```

### Article 404 error
- Check slug spelling in URL
- Verify article was committed to git
- Check Vercel deployment logs

---

## Content Guidelines

### Do
- ✅ Write 2,000-4,000 words for featured articles
- ✅ Include specific technical details
- ✅ Add your "hot take" section
- ✅ Link to original sources
- ✅ Use proper HTML formatting

### Don't
- ❌ Copy-paste press releases
- ❌ Write generic summaries
- ❌ Forget the hot take
- ❌ Use clickbait titles
- ❌ Skip fact-checking

---

## Example: Full Article Script

See: `create_terafab_article.py` in repo for working example.

---

## Emergency Contacts

If GoldmanSax forgets everything:
- This file: `~/workspace/AGENTBEAR_PUBLISHING_GUIDE.md`
- Database: `~/Documents/agentbearcorps/news.db`
- Site URL: https://agentbearcorps.com

---

*Last updated: March 15, 2026*
*AgentBear Corps Publishing Protocol 🐻📰*
