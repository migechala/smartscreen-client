import base64
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import os

import datetime as dt
from dateutil import tz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def convert_time(time, timezone):

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone)
    utc = dt.datetime.strptime(time, '%H:%M')
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone).time()


def get_events(user_id):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        print("creds not valid")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        timezone = service.settings().get(
            setting='timezone').execute()['value']

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            yield(" ", "No events!")
        for event in events:
            start = str(event['start'].get(
                'dateTime', event['start'].get('date')))
            time = str(convert_time(
                start[start.find('T') + 1: start.find('T') + 5], timezone))
            start = start.replace(start[start.find('T'):], " at: " + time)
            yield(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)


hostName = "192.168.1.167"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def _getFiles(self) -> dict:
        file = {}
        path_of_the_directory = 'images'
        ext = ('.jpg', '.png', '.jpeg', '.HELM')
        for files in os.listdir(path_of_the_directory):
            if files.endswith(ext):
                p = self._parseFile(files)
                f = open(path_of_the_directory + '/' + files, "rb")
                file[p["id"]] = [p["answer"],
                                 base64.urlsafe_b64encode(f.read())]
                f.close()
        return file

    base64.urlsafe_b64encode

    def _set_headers(self):
        self.send_response(200, "Ok!")
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.player_count += 1
        print(self.player_count)

    def do_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length),
                keep_blank_values=True)
        else:
            postvars = {}
        user = postvars[b"user"][0].decode("utf-8")
        data = get_events()
        self._set_headers()

        self.wfile.write(data)

        return

    def do_PUT(self):
        self.do_POST()
