import requests
import random
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import csv
import datetime
import os
from supabase import create_client, Client



# Initialize Flask app
app = Flask(__name__)



# YouTube API key (replace with your own key) YOUTUBE API KEY
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")#'AIzaSyCfkyIgJdH3AsG2UB7xLJoHJfO5XH4yCUM'

# Supabase URL and Key (replace with your own)
SUPABASE_URL = os.environ.get("SUPABASE_URL")#SUPABASE_URL
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")#'supabase-key'
# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


#Search for funny vids and skits
SEARCH_QUERY = [
    "funny comedy Videos",
    "Dlip Factory",
    "ASMR Videos",
]

MAX_RESULTS = 3





# Function to log user activity to Supabase
def log_to_supabase(user_number, message):
    # Log user activity to Supabase
    try:
        data = {
            "user_number": user_number,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        res = supabase.table("user_logs").insert({
            "number": "+233555000999",
            "message": "This is a test message"
        }).execute()
        response = supabase.table("user_logs").insert(data).execute()
        if response.status_code == 201:
            print(f"user logged for {user_number}: {message}, response: {response.data}")
        else:
            print(f"Failed to log user: {response}")
    except Exception as e:
        print(f"Error logging to Supabase: {e}")









#Extract video details from YouTube API
def youtube_response(search_word):
    # If no search word is provided, choose a random one from the list
    print(f"Searching for: {search_word}")
    search_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults={MAX_RESULTS}&q={search_word}"
        f"&type=video&key={YOUTUBE_API_KEY}"
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
def log_user_activity(filename,user_number, message):
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
        writer.writerow([row_count, user_number, message, datetime.datetime.now()])
        print(f"Logged activity for {user_number}: {message}")










# Transform and print video data
def transform_video_data(videos):
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
    video_list = transform_video_data(videos)
    

    #building the response
    user_number = request.form.get("From")
    print(f"Received message from {user_number}")
    incoming_msg = request.form.get('Body', '').strip().lower()
    
    
    #get user number
    resp = MessagingResponse()
    msg = resp.message()
    
    # Log user activity to Supabase
    log_to_supabase(user_number, incoming_msg)
    
    
    
    # Log user activity
    log_user_activity('user_activity_log.csv', user_number, incoming_msg)
    
    if "more" in incoming_msg:
        if video_list:
            msg.body("Here are some more funny videos for you to enjoy!\n" + "\n\n".join(video_list))
        else:
            msg.body("Sorry, couldn't find any funny videos at the moment. "
                     "Please try again later or ask for something else.")
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
    return "Clean Dopamine Launcher is running!"

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)  # Set debug=True for development