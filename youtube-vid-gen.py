import requests
import random

API_KEY = 'AIzaSyCfkyIgJdH3AsG2UB7xLJoHJfO5XH4yCUM'

#Search for funny vids and skits
SEARCH_QUERY = [
    "funny comedy Videos",
    "Dlip Factory",
    "ASMR Videos",
]

MAX_RESULTS = 5

#Extract video details from YouTube API
def youtube_response():

    search_word = random.choice(SEARCH_QUERY)
    print(f"Searching for: {search_word}")
    search_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults={MAX_RESULTS}&q={search_word}"
        f"&type=video&key={API_KEY}"
    )

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        search_response = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from YouTube API: {e}") 
        return
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return
    
    videos = search_response.get("items", [])
    return videos if videos else None


# Transform and print video data
def Transform_video_data(videos):
    if not videos:
        print("No videos found.")
        return
    
    for video in videos:
        title = video['snippet']['title']
        channel = video['snippet']['channelTitle']
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
            
        print(f"Title: {title}")
        print(f"Channel: {channel}")
        print(f"Video URL: {video_url}")
        print("-" * 60)
    
    return videos
            
def main():
    videos = youtube_response()
    Transform_video_data(videos)
    print("Searching for funny videos...")
    youtube_response()
if __name__ == "__main__":
    main()