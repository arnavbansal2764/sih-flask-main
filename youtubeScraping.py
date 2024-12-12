from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

def youtube_search(query, api_key):
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Perform the search
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=10  # Number of results to fetch
    ).execute()

    # Extract video details
    videos = []
    for item in search_response['items']:
        video = {
            'title': item['snippet']['title'],
            'videoId': item['id']['videoId'],
            'description': item['snippet']['description'],
            'publishedAt': item['snippet']['publishedAt'],
            'channelTitle': item['snippet']['channelTitle'],
            'thumbnailUrl': item['snippet']['thumbnails']['default']['url']
        }
        videos.append(video)

    return videos

# Example usage
api_key = os.environ["YOUTUBE_API_KEY"]  # Replace with your YouTube API key
search_query = 'Data science'

videos = youtube_search(search_query, api_key)

# Displaying the results
for video in videos:
    print(f"Title: {video['title']}")
    print(f"Video URL: https://www.youtube.com/watch?v={video['videoId']}")
    print(f"Description: {video['description']}")
    print(f"Published on: {video['publishedAt']}")
    print(f"Channel: {video['channelTitle']}")
    print(f"Thumbnail: {video['thumbnailUrl']}")
    print("-" * 50)