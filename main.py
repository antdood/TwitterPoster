import schedule
import time
import randomSelector
import ImageDownloader
import twitterPoster
import os

from dotenv import load_dotenv

load_dotenv()

def findAndTweetMedia():
	media_infos = ImageDownloader.GetFiles(os.getenv('FOLDER_ID'))

	media_names = [media["name"] for media in media_infos]

	selected_media_name = randomSelector.selectRandom(media_names)

	selected_media_info = next(media for media in media_infos if media["name"] == selected_media_name)

	selected_media_path = ImageDownloader.DownloadFile(selected_media_info)

	with open(selected_media_path) as selected_media:
		twitterPoster.tweet("", [selected_media])

findAndTweetMedia()