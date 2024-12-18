from flask import Flask, render_template, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400
    
    try:
        # Fetch the content from the target URL
        response = requests.get(url)
        
        # Forward the content with necessary headers
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers['content-type']
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 