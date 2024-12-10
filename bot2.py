from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
import json
import os
import yt_dlp
import schedule
from datetime import datetime
from dotenv import load_dotenv
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Constants
VIDEOS_DIR = "videos_bot2"  # Different directory to avoid conflicts with bot.py
TRACKED_URLS_FILE = "tracked_urls_bot2.json"
UPLOADED_VIDEOS_FILE = "uploaded_videos_bot2.json"
TIKTOK_PROFILE = os.getenv("TIKTOK_PROFILE2")

# YouTube API Constants
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secrets.json"
CREDENTIALS_PICKLE_FILE = 'youtube_token.pickle'

if not TIKTOK_PROFILE:
    raise ValueError("TikTok profile URL not found in environment variables (TIKTOK_PROFILE2)!")

def ensure_directory_exists():
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR)

def load_tracked_urls():
    if os.path.exists(TRACKED_URLS_FILE):
        with open(TRACKED_URLS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded_urls": []}

def save_tracked_urls(urls_data):
    with open(TRACKED_URLS_FILE, 'w') as f:
        json.dump(urls_data, f, indent=4)

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(VIDEOS_DIR, '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extractor_args': {
            'tiktok': {
                'download_without_watermark': True,
                'use_api': False
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Successfully downloaded: {url}")
            return True
    except Exception as e:
        print(f"Error downloading video {url}: {e}")
        return False

def setup_chrome_options():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-features=NetworkService')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    return chrome_options

def create_stealth_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    
    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error creating driver: {e}")
        return None

def get_video_urls(driver, num_videos=10):
    video_urls = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(video_urls) < num_videos:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Get all video links
        elements = driver.find_elements(By.TAG_NAME, "a")
        for element in elements:
            href = element.get_attribute("href")
            if href and "/video/" in href and href not in video_urls:
                video_urls.append(href)
                if len(video_urls) >= num_videos:
                    break
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    return video_urls[:num_videos]

def get_authenticated_service():
    credentials = None
    
    if os.path.exists(CREDENTIALS_PICKLE_FILE):
        with open(CREDENTIALS_PICKLE_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open(CREDENTIALS_PICKLE_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    
    return build('youtube', 'v3', credentials=credentials)

def upload_to_youtube(video_file):
    try:
        youtube = get_authenticated_service()
        
        # Generate title from filename
        title = os.path.splitext(os.path.basename(video_file))[0]
        title = f"#shorts {title}"
        
        body = {
            'snippet': {
                'title': title,
                'description': "",
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }

        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )

        print(f'Uploading to YouTube: {video_file}...')
        response = insert_request.execute()
        print(f'YouTube upload complete! Video ID: {response["id"]}')
        
        # Mark as uploaded
        if os.path.exists(UPLOADED_VIDEOS_FILE):
            with open(UPLOADED_VIDEOS_FILE, 'r') as f:
                uploaded_videos = json.load(f)
        else:
            uploaded_videos = []
        
        uploaded_videos.append(video_file)
        with open(UPLOADED_VIDEOS_FILE, 'w') as f:
            json.dump(uploaded_videos, f, indent=4)
            
        return True

    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred: {e.content}')
        return False
    except Exception as e:
        print(f'An error occurred during YouTube upload: {e}')
        return False

def process_new_videos(video_urls):
    tracked_urls = load_tracked_urls()
    downloaded_urls = tracked_urls["downloaded_urls"]
    new_videos_downloaded = 0
    
    for url in video_urls:
        if url not in downloaded_urls:
            print(f"New video found: {url}")
            if download_video(url):
                downloaded_urls.append(url)
                new_videos_downloaded += 1
                tracked_urls["downloaded_urls"] = downloaded_urls
                save_tracked_urls(tracked_urls)
                print(f"Successfully downloaded video: {url}")
                
                # Find the downloaded video file
                for filename in os.listdir(VIDEOS_DIR):
                    if filename.endswith(('.mp4', '.webm')):
                        video_path = os.path.join(VIDEOS_DIR, filename)
                        
                        # Check if video was already uploaded
                        if os.path.exists(UPLOADED_VIDEOS_FILE):
                            with open(UPLOADED_VIDEOS_FILE, 'r') as f:
                                uploaded_videos = json.load(f)
                        else:
                            uploaded_videos = []
                        
                        if video_path not in uploaded_videos:
                            print(f"Uploading to YouTube: {video_path}")
                            if upload_to_youtube(video_path):
                                print("Waiting 30 minutes before next operation...")
                                time.sleep(1800)  # Wait 30 minutes
                            else:
                                print("YouTube upload failed, will retry next time")
            else:
                print(f"Failed to download video: {url}")
    
    return new_videos_downloaded

def visit_tiktok_profile():
    print(f"\nStarting TikTok profile visit at {datetime.now()}")
    driver = None
    
    try:
        driver = create_stealth_driver()
        if not driver:
            print("Failed to create driver")
            return
        
        try:
            time.sleep(random.uniform(2, 4))
            driver.get(TIKTOK_PROFILE)
            time.sleep(3)
            
            for _ in range(3):
                try:
                    video_urls = get_video_urls(driver)
                    if video_urls:
                        break
                    time.sleep(2)
                except Exception as e:
                    print(f"Error getting video URLs (attempt {_ + 1}): {e}")
                    time.sleep(2)
            
            if video_urls:
                new_videos = process_new_videos(video_urls)
                print(f"Downloaded {new_videos} new videos")
            else:
                print("No video URLs found")
                
        except Exception as e:
            print(f"Error during TikTok profile visit: {e}")
            
    finally:
        if driver:
            driver.quit()
    
    print("Profile visit completed")

def job():
    print(f"\nStarting job at {datetime.now()}")
    try:
        ensure_directory_exists()
        visit_tiktok_profile()
    except Exception as e:
        print(f"Error during job execution: {e}")
    
    print("Job completed")

def main():
    # Run job immediately once
    job()
    
    # Schedule job to run every 12 hours
    schedule.every(12).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
