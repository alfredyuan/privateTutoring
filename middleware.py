import httplib2
import pprint
import sys
from google.appengine.api import memcache
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import mail
from pyrfc3339 import parse

calId = 'YOUR GOOGLE CALENDAR ID'

def initService():

  api_key = 'YOUR GOOGLE API KEY'

  credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/calendar')
  http = httplib2.Http(memcache)
  http = credentials.authorize(http)

  service = build("calendar", "v3", http=http, developerKey=api_key)

  return service

def listAllEvents():
  # List all the tasklists for the account.
  service = initService()

  events = service.events().list(calendarId=calId).execute()
  
  return events

def gCal(event):
  cal = Calendar()
  from datetime import datetime

  event = Event()
  event.add('summary', 'Private Tutoring: '+ event['summary'])
  event.add('dtstart', )

def updateEvent(evt_id, user_str, mail_list):
  service = initService()
  event = service.events().get(calendarId=calId, eventId=evt_id).execute()

  #return event['id']
  creator_email = event['creator']['email']
  creator = event['summary']

  if event.has_key('description') and event['description'].strip() != '':
    return 'RESERVED'

  event['description'] = user_str

  update_event = service.events().update(calendarId=calId, eventId=event['id'], body=event).execute()

  mail_list.append(creator_email)

  dtstart = parse(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M:%S')
  dtend = parse(event['end']['dateTime']).strftime('%Y-%m-%d %H:%M:%S')

  for x in mail_list:
    if x.strip() != '':
      mail.send_mail(sender=creator_email, 
                        to=x,
                        subject="Confirmation of Private Tutoring Reservation",
                        body="""
      Hi,

      Instructor: %(instructor)s
      Start Time: %(dtstart)s
      End Time: %(dtend)s
      Participants: %(partici)s

      This mail confirms you that your request of Private Tutoring
      has been received by GSI. Once location is determined, GSI 
      will contact you with details.

      Best,

      %(creator)s
      """ % {'instructor':creator, 
            'dtstart':dtstart,
            'dtend':dtend,
            'partici':user_str,
            'creator':creator})

  return 'RESERVE_OK'

def cancelEvent(evt_id, user_list, mail_list):
  service = initService()
  event = service.events().get(calendarId=calId, eventId=evt_id).execute()

  if not event.has_key('description') or event['description'].strip() == '':
    return 'CANCEL_NULL'

  user_str = event['description']

  for x in user_list:
    if user_str.find(x) != -1:
      event['description'] = ''
      update_event = service.events().update(calendarId=calId, eventId=event['id'], body=event).execute()
      
      creator_email = event['creator']['email']
      creator = event['summary']
      
      mail_list.append(creator_email)

      dtstart = parse(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M:%S')
      dtend = parse(event['end']['dateTime']).strftime('%Y-%m-%d %H:%M:%S')

      for x in mail_list:
        if x.strip() != '':
          mail.send_mail(sender=creator_email, 
                            to=x,
                            subject="Cancelation of Private Tutoring Reservation",
                            body="""
          Hi,

          Instructor: %(instructor)s
          Start Time: %(dtstart)s
          End Time: %(dtend)s
          Participants: %(partici)s

          This mail confirms you that your request of Private Tutoring
          has been canceled.

          Best,

          %(creator)s
          """ % {'instructor':creator, 
                'dtstart':dtstart,
                'dtend':dtend,
                'partici':user_str,
                'creator':creator})

      return 'CANCEL_OK'
  
  return 'CANCEL_INVALID'
