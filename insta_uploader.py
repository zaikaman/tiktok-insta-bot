from instagrapi import Client
import os
import json
import time
from datetime import datetime
import moviepy.editor as mp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VIDEOS_DIR = os.getenv("VIDEOS_DIR", "videos")
POSTED_URLS_FILE = os.getenv("POSTED_URLS_FILE", "posted_urls.json")

def load_posted_urls():
    if os.path.exists(POSTED_URLS_FILE):
        with open(POSTED_URLS_FILE, 'r') as f:
            return json.load(f)
    return {"posted_urls": []}

def save_posted_urls(urls_data):
    with open(POSTED_URLS_FILE, 'w') as f:
        json.dump(urls_data, f, indent=4)

def validate_video(video_path):
    try:
        video = mp.VideoFileClip(video_path)
        duration = video.duration
        video.close()
        
        if duration > 90:
            print(f"Warning: Video duration ({duration}s) exceeds Instagram limit (90s)")
        return True
    except Exception as e:
        print(f"Error validating video: {e}")
        return False

def upload_single_video(cl, video_path, caption):
    max_retries = 3
    retry_count = 0
    
    if not validate_video(video_path):
        print("Video validation failed")
        return False
    
    while retry_count < max_retries:
        try:
            print(f"Attempting upload (try {retry_count + 1}/{max_retries})")
            
            media = cl.clip_upload(
                video_path,
                caption=caption,
                extra_data={
                    "custom_accessibility_caption": "",
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False
                }
            )
            
            if media:
                print("Upload successful!")
                return True
                
        except Exception as e:
            print(f"Error on attempt {retry_count + 1}: {e}")
        
        retry_count += 1
        if retry_count < max_retries:
            print(f"Waiting 30 seconds before retry...")
            time.sleep(30)
    
    return False

def upload_to_instagram(username, password):
    if not username or not password:
        raise ValueError("Instagram credentials not provided!")
        
    cl = Client()
    
    try:
        print(f"Logging in as {username}...")
        cl.login(username, password)
        
        posted_data = load_posted_urls()
        posted_urls = posted_data["posted_urls"]
        
        video_files = []
        for file in os.listdir(VIDEOS_DIR):
            if file.endswith('.mp4'):
                full_path = os.path.join(VIDEOS_DIR, file)
                if file not in posted_urls:
                    video_files.append(full_path)
        
        if not video_files:
            print("No new videos to upload")
            return
        
        total_videos = len(video_files)
        print(f"\nFound {total_videos} new videos to upload")
        
        for index, video_path in enumerate(video_files, 1):
            try:
                print(f"\nUploading video {index}/{total_videos}")
                print(f"Video path: {video_path}")
                
                caption = f"🎥✨ #reels #trending #viral #music #cover"
                
                if upload_single_video(cl, video_path, caption):
                    print(f"Upload successful for video {index}!")
                    posted_urls.append(os.path.basename(video_path))
                    save_posted_urls(posted_data)
                else:
                    print(f"Upload failed for video {index} after all retries!")
                
                if index < total_videos:
                    print(f"Waiting 1 hour before uploading next video...")
                    time.sleep(3600)
                
            except Exception as e:
                print(f"Error uploading video {index} ({video_path}): {e}")
        
        print("\nUpload session completed!")
        
    except Exception as e:
        print(f"Error during Instagram session: {e}")
        
    finally:
        try:
            cl.logout()
        except:
            pass

if __name__ == "__main__":
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("INSTA_PASSWORD")
    
    if not username or not password:
        raise ValueError("Instagram credentials not found in environment variables!")
        
    upload_to_instagram(username, password)
