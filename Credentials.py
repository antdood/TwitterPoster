import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

class Credential:
	creds = None
	SCOPES = [os.getenv('SCOPES')]

	@classmethod
	def InitCredentials(cls):
		if os.path.exists('token.json'):
			return Credentials.from_authorized_user_file('token.json', cls.SCOPES)

	@classmethod
	def IsCredsValid(cls):
		if not cls.creds or not cls.creds.valid:
			return False

		return True

	@classmethod
	def RefreshCreds(cls):
		if not cls.creds:
			cls.creds = cls.InitCredentials()

		if cls.creds and cls.creds.expired and cls.creds.refresh_token:
			cls.creds.refresh(Request())
			
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', cls.SCOPES)
			cls.creds = flow.run_local_server(port=0)

	@classmethod
	def GetCredentials(cls):
		if not cls.IsCredsValid():
			cls.RefreshCreds()

		return cls.creds
