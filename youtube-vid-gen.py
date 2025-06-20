import requests
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import csv
import datetime

# Initialize Flask app
app = Flask(__name__)


# YouTube API key (replace with your own key) YOUTUBE API KEY
API_KEY = ''


#Search for funny vids and skits
SEARCH_QUERY = [
    "funny comedy Videos",
    "Dlip Factory",
    "ASMR Videos",
]

MAX_RESULTS = 3



#Extract video details from YouTube API
def youtube_response(search_word):
    # If no search word is provided, choose a random one from the list
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
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return []
    
    videos = search_response.get("items", [])
    return videos if videos else []



#log user activity to a CSV file
def log_user_activity(filename,user_number, message,date):
    #create a new line in the CSV file with user number and message
    #if the file does not exist, create it and write the header
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            row_count = sum(1 for row in file) + 1
    except FileNotFoundError:
        row_count = 1
    
    #log the user activity
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([row_count, user_number, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        print(f"Logged activity for {user_number}: {message}")






# Transform and print video data
def Transform_video_data(videos):
    results = []
    if not videos:
        print("No videos found.")
        return []
    
    for video in videos:
        try:
            title = video['snippet']['title']
            channel = video['snippet']['channelTitle']
            video_id = video['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            results.append(f"{title} by {channel}: {video_url}")
            print(f"Title: {title}")
            print(f"Channel: {channel}")
            print(f"Video URL: {video_url}")
            print("-" * 60)
        except KeyError:
            continue
    return results




# Flask route to handle incoming messages
@app.route("/webhook", methods=["POST"])      
def dopamine_reply():


    search_word=random.choice(SEARCH_QUERY)
    videos = youtube_response(search_word)
    print("Searching for funny videos...")
    video_list = Transform_video_data(videos)
    

    #building the response
    user_number = request.form.get("From")
    print(f"Received message from {user_number}")
    incoming_msg = request.form.get('Body', '').strip().lower()
    
    #get user number
    resp = MessagingResponse()
    msg = resp.message()
    
    # Log user activity
    log_user_activity('user_activity_log.csv', user_number, incoming_msg, datetime.datetime.now())
    
    if "more" in incoming_msg:
        msg.body("Here are some more funny videos for you to enjoy!\n" + "\n".join(video_list))
    elif "help" in incoming_msg:
        msg.body("Clean Dopamine is all about providing you with "
                 "positive and uplifting content. "
                 "We focus on sharing funny videos, ASMR, and other "
                 "content that brings joy and relaxation. "
                 "Feel free to ask for more videos or any help you need!")
    else:
        msg.body("Welcome to the Clean Dopamine channel! "
                 "Type: \n"
                 "'more'- For Clean Dopamine Videos(Funny, ASMR) \n"
                 "'help'- to understand what Clean Dopamine is all About \n"
        
                 )
    print(f"From {user_number} — Message: {incoming_msg}")
    return str(resp)



@app.route("/")
def home():
    return "🚀 Clean Dopamine Launcher is running!"

    
if __name__ == "__main__":
    app.run(port=8080, debug=True)