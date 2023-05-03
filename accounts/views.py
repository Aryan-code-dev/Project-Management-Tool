from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from cal.models import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


# Create your views here.


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        designation = request.POST['designation']
        print(designation)
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('accounts:signin')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('accounts:signin')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('accounts:signin')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('accounts:signin')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('accounts:signin')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        
        myuser.is_active = True
        
        myuser.save()
        u = UserProfile.objects.get(user_id=myuser.id)
        u.designation = designation
        u.save()
        messages.success(request, "Your Account has been created succesfully!! ")
        
        
        return redirect('accounts:signin')
        
        
    return render(request, "accounts/signup.html")

def logout(request):
    del request.session['authenticated']
    del request.session['designation']
    del request.session['user_id']
    messages.success(request, "Logged Out Successfully!!")
    return redirect('accounts:signin')


def signin(request):
   
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        desig = request.POST['designation']
        
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.username
            messages.success(request, "Logged In Sucessfully!!")
            request.session["authenticated"] = True
            request.session["user_id"] = user.id
            request.session["designation"] = desig
            if desig=="Project Manager":  
                #return render(request, "cal/templates/calcalendar.html",{"fname":fname})
                return redirect('accounts:M_homepage')
            else:
                return redirect(request,'accounts:E_homepage')
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('accounts:signin')
    
    return render(request, "accounts/signin.html")


# def signout(request):
#     logout(request)
#     messages.success(request, "Logged Out Successfully!!")
#     return redirect('accounts:signin')

def m_homepage(request):
    if request.session["authenticated"] == True and request.session["designation"]=="Project Manager":

        return render(request, "accounts/Mhomepage.html", {"user_id" : request.session['user_id']})

def e_homepage(request):
    if request.session["authenticated"] == True and request.session["designation"]=="Employee":
        return render(request, "accounts/Ehomepage.html")
    

def eventdata(request):
    print("hello")
    if request.method == 'POST':
        summ =  request.POST['event_summ']
        loc =  request.POST['event_loc']
        desc = request.POST['event_desc']
        start = request.POST['event_start']
        end = request.POST['event_end']
        mail = request.POST.get('emp_emails')

        # print((mail))

        attendees = mail.split(',')

        for i in attendees:
            print(i)

        # event = {}
        # event['summary'] = summ
        # event['location'] = loc
        # event['description'] = desc
        # event['start'] = summ
        # event['summary'] = summ
        # event['summary'] = summ
        # event['summary'] = summ


        event = {
            'summary': summ,
            'location': loc,
            'description': desc,
            'start': {
                'dateTime': start,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': attendees},
                
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        print(event['start'])
        print(event['end'])
        print(event['attendees'])
        create_events(request,event)
        return render(request, 'accounts/eventdata.html')    

    return render(request, 'accounts/eventdata.html')    



def get_credentials(request):
        user_id = request.session.get('user_id')
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

def create_events(request,event):
    creds = get_credentials(request)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            
            creds.refresh(Request())
        else:
            print("creds expired")
            flow = InstalledAppFlow.from_client_secrets_file(
                'cal/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            user_id = request.session.get('user_id')
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
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))