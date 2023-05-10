from __future__ import print_function
from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import datetime
from .models import *
from .utils import Calendar
from .forms import EventForm
SCOPES = ['https://www.googleapis.com/auth/calendar']
def index(request):
    return HttpResponse('hello')

class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        #print(d.year,d.month,d.day)
        cal = Calendar(d.year, d.month,d.day)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        print(context['prev_month'])
        print(context['next_month'])
        if self.request.session["authenticated"] == True:
            return context

def get_date(req_month):
    if req_month:
        print(req_month)
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request, event_id=None):
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()

    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        print(form)
        form.save()
        if request.session["authenticated"] == True:
             
            return HttpResponseRedirect(reverse('cal:calendar'))
    return render(request, 'cal/event.html', {'form': form})


class CalendarView1(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_credentials(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                credentials = GoogleCalendar.objects.get(user=user)
                creds = Credentials.from_authorized_user_info(info={
                    'access_token': credentials.access_token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': '349783946598-skhvjocccpn901vh3jcqu7qvkc2cv85k.apps.googleusercontent.com',
                    'client_secret': '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',
                    'expiry': credentials.token_expiry.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + "Z" if credentials.token_expiry else None,


                })
                return creds
            except User.DoesNotExist:
                pass
            except GoogleCalendar.DoesNotExist:
                pass

        return None

    def get_events(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = self.get_credentials()
        if not creds or not creds.valid:
            if creds and not creds.expired:
                
                creds.refresh(Request())
            else:
                print("creds expired")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'cal/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                user_id = self.request.session.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        credentials = GoogleCalendar.objects.get_or_create(user=user)[0]
                        credentials.access_token = creds.token
                        credentials.refresh_token = creds.refresh_token
                        credentials.token_expiry = creds.expiry
                        credentials.save()
                    except User.DoesNotExist:
                        pass

        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
                                              
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        
        # Prints the start and name of the next 10 events
        for event in events:
            # print(Event.objects.filter(title = event['summary'],description=event['summary'],start_time=event['start']['dateTime'],end_time=event['end']['dateTime']))
            if not Event.objects.filter(title = event['summary'],description=event['summary'],start_time=event['start']['dateTime'].split('+')[0],end_time=event['end']['dateTime'].split('+')[0]):
                # a = Event.objects.filter(start_time=event['start']['dateTime'])
                # b = Event.objects.filter(end_time=event['end']['dateTime'])
                print(event['start']['dateTime'],event['end']['dateTime'])
                event_instance = Event()
                event_instance.title=event['summary']   
                event_instance.description=event['summary']
                event_instance.start_time=event['start']['dateTime'].split('+')[0]
                event_instance.end_time=event['end']['dateTime'].split('+')[0]
                event_instance.save()

        #return CalendarView.get_context_data
        # except HttpError as error:
        #     print('An error occurred: %s' % error)

    def get_context_data(self, **kwargs):
        self.get_events()
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month,d.day)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        if self.request.session["authenticated"] == True:
                return context


