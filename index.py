# Vercel serverless entry point
from news_app import app

# This is required for Vercel serverless functions
def handler(request, **kwargs):
    return app(request.environ, kwargs.get('start_response'))
