from flask import Flask, request, jsonify, send_from_directory
import googleapiclient.discovery
from flask_cors import CORS 
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import googleapiclient.discovery
import pandas as pd
from dotenv import load_dotenv
import os 


load_dotenv()
nltk.download('vader_lexicon')

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyAzwbV218-p1PgZT6GU6oVerIxDaQ2C-Zw"

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')

@app.route('/')

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files (CSS, JS)."""
    return send_from_directory('.', path)

def extract_video_id(video_url):
    """Extract video ID from various YouTube URL formats."""
    import re
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    return None

@app.route('/analyze', methods=['POST'])
def analyze_comments():
    """Analyze YouTube comments for sentiment."""
     # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        video_url = data.get('videoUrl')
        if not video_url:
            return jsonify({'error': 'Video URL is required'}), 400
        
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, 
            API_VERSION, 
            developerKey=DEVELOPER_KEY
        )

        comments = []
        next_page_token = None
        
        while len(comments) < 1000:
            request_params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': 100,  # Changed to 100 for better pagination
                'textFormat': 'plainText'
            }
            
            if next_page_token:
                request_params['pageToken'] = next_page_token
                
            response = youtube.commentThreads().list(**request_params).execute()
            
            items = response.get('items', [])
            if not items:
                break
                
            for item in items:
                comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment_text)
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        if not comments:
            return jsonify({
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total_comments': 0,
                'message': 'No comments found for this video'
            }), 200

        # Perform sentiment analysis
        sia = SentimentIntensityAnalyzer()
        sentiments = [sia.polarity_scores(comment)['compound'] for comment in comments]
        
        # Classify sentiments
        labels = ['positive' if s > 0.05 
                 else 'negative' if s < -0.05 
                 else 'neutral' for s in sentiments]
        
        # Count sentiments
        sentiment_counts = pd.Series(labels).value_counts()
        
        return jsonify({
            'positive': int(sentiment_counts.get('positive', 0)),
            'neutral': int(sentiment_counts.get('neutral', 0)),
            'negative': int(sentiment_counts.get('negative', 0)),
            'total_comments': len(comments)
        })

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
