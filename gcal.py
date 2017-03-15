
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'gcal.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

EVENT = {
  'summary': '{0} ${1}',
  'location': '',
  'description': 'On Southwest. Leaving at: .',
  'start': {
    'date': '{2}',
    'timeZone': 'America/Chicago',
  },
  'end': {
    'date': '{3}',
    'timeZone': 'America/Chicago',
  },
}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create(destination, cost, departure_date, return_date):
    """Creates gCal Event."""
    departure_date = datetime.datetime.strptime(departure_date, '%m/%d/%Y').strftime('%Y-%m-%d')
    return_date = datetime.datetime.strptime(return_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    EVENT['summary'] = '{0} ${1}'.format(destination, cost)
    EVENT['start']['date'] = departure_date
    EVENT['end']['date'] = return_date

    # Add event
    event = service.events().insert(calendarId='hvshhftv62u0qst16np8las1ek@group.calendar.google.com',
                                    body=EVENT).execute()
    return event.get('id')

def update(destination, cost, departure_date, return_date, gcalEventId):
    "Updates an existing event"
    departure_date = datetime.datetime.strptime(departure_date, '%m/%d/%Y').strftime('%Y-%m-%d')
    return_date = datetime.datetime.strptime(return_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # Check if event exists
    try:
        service.events().get(calendarId='hvshhftv62u0qst16np8las1ek@group.calendar.google.com',
                             eventId=gcalEventId).execute()
    except errors.HttpError:
        return create(destination, cost, departure_date, return_date)

    EVENT['summary'] = '{0} ${1}'.format(destination, cost)
    EVENT['start']['date'] = departure_date
    EVENT['end']['date'] = return_date
    # Update event
    service.events().update(calendarId='hvshhftv62u0qst16np8las1ek@group.calendar.google.com',
                            eventId=gcalEventId,
                            body=EVENT).execute()

def delete(gcalEventId):
    "Delete an existing event"
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    service.events().update(calendarId='hvshhftv62u0qst16np8las1ek@group.calendar.google.com',
                            eventId=gcalEventId,).execute()
