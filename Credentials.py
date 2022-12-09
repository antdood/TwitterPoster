import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Credential:
	creds = None

	@classmethod
	def InitCredentials(cls, SCOPES):
		if os.path.exists('token.json'):
			return Credentials.from_authorized_user_file('token.json', SCOPES)

	@classmethod
	def CheckCredentialsValidity(cls, SCOPES):
		if not cls.creds or not cls.creds.valid:
			if cls.creds and cls.creds.expired and cls.creds.refresh_token:
				cls.creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', SCOPES)
				cls.creds = flow.run_local_server(port=0)

	@classmethod
	def GetCredentials(cls, SCOPES):
		if not cls.creds:
			cls.creds = cls.InitCredentials(SCOPES)

		cls.CheckCredentialsValidity(SCOPES)

		return cls.creds
