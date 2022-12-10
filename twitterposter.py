import os
import sys
import time

import json
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

oauth = OAuth1(CONSUMER_KEY
				, client_secret = CONSUMER_SECRET
				, resource_owner_key = ACCESS_TOKEN
				, resource_owner_secret = ACCESS_TOKEN_SECRET)

class MediaUploader(object):
	def __init__(self, file):
		self.video_file = file
		self.total_bytes = os.fstat(self.video_file.fileno()).st_size
		self.media_id = None
		self.processing_info = None

	def UploadInit(self):
		request_data = {
			'command': 'INIT',
			'media_type': 'video/mp4',
			'total_bytes': self.total_bytes,
			'media_category': 'tweet_image'
		}

		req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
		media_id = req.json()['media_id']

		self.media_id = media_id

		print('Media ID: %s' % str(media_id))

	def UploadAppend(self):
		segment_id = 0
		bytes_sent = 0

		while bytes_sent < self.total_bytes:
			chunk = self.video_file.read(4*1024*1024)
		  
			print('APPEND')

			request_data = {
				'command': 'APPEND',
				'media_id': self.media_id,
				'segment_index': segment_id
			}

			files = {
				'media':chunk
			}

			req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=oauth)

			if req.status_code < 200 or req.status_code > 299:
				print(req.status_code)
				print(req.text)
				sys.exit(0)

			segment_id = segment_id + 1
			bytes_sent = self.video_file.tell()

			print('%s of %s bytes uploaded' % (str(bytes_sent), str(self.total_bytes)))

			print('Upload chunks complete.')

	def UploadFinalize(self):
		print('FINALIZE')

		request_data = {
			'command': 'FINALIZE',
			'media_id': self.media_id
		}

		req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)

		self.processing_info = req.json().get('processing_info', None)
		self.CheckStatus()

	def CheckStatus(self):
		if self.processing_info is None:
			return

		state = self.processing_info['state']

		print('Media processing status is %s ' % state)

		if state == u'succeeded':
			return

		if state == u'failed':
			sys.exit(0)

		check_after_secs = self.processing_info['check_after_secs']
	
		print('Checking after %s seconds' % str(check_after_secs))
		time.sleep(check_after_secs)

		print('STATUS')

		request_params = {
			'command': 'STATUS',
			'media_id': self.media_id
		}

		req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)
	
		self.processing_info = req.json().get('processing_info', None)
		self.CheckStatus()

	def GetMediaID(self):
		return self.media_id

def tweet(text, medias):
	media_ids_string = ""
	
	for media in medias:
		uploader = MediaUploader(media)
		uploader.UploadInit()
		uploader.UploadAppend()
		uploader.UploadFinalize()
		print(uploader.GetMediaID())
		media_ids_string += f"{uploader.GetMediaID()},"

	request_data = {'status': text
					, 'media_ids': media_ids_string}

	req = requests.post(url = POST_TWEET_URL, data = request_data, auth = oauth)
	
	print(f"tweet with {len(medias)} medias")

if __name__ == '__main__':
	with open(os.path.join("Downloads", "test_img.png"), 'rb') as media:
		tweet('test upload', [media])