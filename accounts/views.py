from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile

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