from flask import Flask, render_template, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

def rewrite_urls(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Rewrite relative URLs to absolute URLs
    for tag in soup.find_all(['link', 'script', 'img', 'a']):
        # Handle href attributes
        if tag.has_attr('href'):
            tag['href'] = urljoin(base_url, tag['href'])
        
        # Handle src attributes
        if tag.has_attr('src'):
            tag['src'] = urljoin(base_url, tag['src'])
        
        # Handle srcset attributes
        if tag.has_attr('srcset'):
            sources = tag['srcset'].split(',')
            new_sources = []
            for source in sources:
                parts = source.strip().split()
                if len(parts) >= 1:
                    parts[0] = urljoin(base_url, parts[0])
                new_sources.append(' '.join(parts))
            tag['srcset'] = ', '.join(new_sources)

    # Add base tag to handle other relative URLs
    base_tag = soup.new_tag('base')
    base_tag['href'] = base_url
    if soup.head:
        soup.head.insert(0, base_tag)
    
    return str(soup)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400
    
    try:
        # Set up headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Fetch the content from the target URL
        response = requests.get(url, headers=headers)
        content_type = response.headers.get('content-type', '')
        
        # Only process HTML content
        if 'text/html' in content_type.lower():
            modified_content = rewrite_urls(response.text, url)
            return Response(
                modified_content,
                status=response.status_code,
                content_type='text/html'
            )
        else:
            # For non-HTML content (images, css, js, etc.), pass through as-is
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers['content-type']
            )
            
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 