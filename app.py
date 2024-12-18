from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.after_request
def after_request(response):
    # Add CORS and caching headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    return response

@app.route('/')
def index():
    logger.info('Serving index page')
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    logger.info(f'Proxy request for URL: {url}')
    
    if not url:
        logger.error('No URL provided')
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache'
        }
        
        logger.info('Sending request to target URL')
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Log response details
        logger.info(f'Response status: {response.status_code}')
        logger.info(f'Response encoding: {response.encoding}')
        logger.info(f'Response headers: {dict(response.headers)}')
        
        # Ensure proper encoding
        response.encoding = response.apparent_encoding
        content = response.text
        
        # Log content length
        logger.info(f'Content length: {len(content)}')
        
        return content
        
    except requests.exceptions.RequestException as e:
        logger.error(f'Request error: {str(e)}')
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f'Starting server on port {port} with debug={debug}')
    app.run(host='0.0.0.0', port=port, debug=debug) 