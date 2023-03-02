from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import datetime
import bcrypt

todays_date = datetime.datetime.now()

# -------------------------------------------- LOGIN AND REGISTRATION
def register(request):
    return render(request, "register.html")

def create_user(request):
    if request.method == "POST":
        errors = User.objects.user_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect('/register')
        else:
            password = request.POST['password']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            secret_a = request.POST['secret_answer']
            sa_hash = bcrypt.hashpw(secret_a.encode(), bcrypt.gensalt()).decode()
            User.objects.create(first_name = request.POST["first_name"].title(),last_name = request.POST["last_name"].title(),email = request.POST["email"],dob = request.POST["dob"], password = pw_hash, secret_question = request.POST['secret_question'], secret_answer = sa_hash)
            logged_in_user = User.objects.get(email=request.POST['email'])
            request.session['id'] = logged_in_user.id
    return redirect('/dashboard')

def login(request):
    return render(request, "login.html")

def login_user(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect('/login')
    logged_in_user = User.objects.get(email=request.POST['email'])
    request.session['id'] = logged_in_user.id
    return redirect('/dashboard')

def logout(request):
    del request.session
    return redirect('/login')

# --------------------------------------------------- FORGOT PASSWORD
def forgot_password(request):
    return render(request, "forgot_password.html")

# first step of reset password, determining who the user is
def find_email(request):
    if request.method == "POST":
        errors = User.objects.email_finder_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect('/forgot_password')
    user_reset_pw = User.objects.get(email=request.POST['email'])
    id = user_reset_pw.id
    return redirect(f'/secret_q/{id}')

# second step of reset password, pulling up their secret question
def secret_q(request,id):
    user = User.objects.get(id=id)
    context = {
        'secret_question' : user.secret_question,
        'user_id' : user.id
    }
    return render(request, 'secret_q.html', context)

# third step of reset password, checking for a match with their secret answer
def answer_secret_q(request):
    if request.method == "POST":
        errors = User.objects.secret_q_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect('/forgot_password')
    user_reset_pw = User.objects.get(id=request.POST['user_id'])
    id = user_reset_pw.id
    return redirect(f'/reset_password/{id}')

# fourth step of reset password, loading password update page
def reset_password(request, id):
    user = User.objects.get(id=id)
    context = {
        'user_id' : user.id
    }
    return render(request, 'reset_password.html', context)

# last step, making the password change
def resetting_forgotten_password(request):
    if request.method == "POST":
        errors = User.objects.reset_password_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect('/forgot_password')
        else:
            password = request.POST['password']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = User.objects.get(id=request.POST['user_id'])
            user.password = pw_hash
            user.save()
    return redirect('/login')

# -------------------------------------------- VIEW AND UPDATE USER
def view_account(request, id):
    id = request.session['id']
    user = User.objects.get(id=id)
    date = user.dob.strftime('%Y-%m-%d')
    context = {
        'user' : user,
        'date' : date,
    }
    return render (request, 'user_profile.html', context)

def update_user(request, id):
    id = request.session['id']
    if request.method == "POST":
        user_to_update = User.objects.get(id=id)
        errors = User.objects.user_update_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect(f'/account/{id}')
        else:
            password = request.POST['new_password']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            secret_a = request.POST['secret_answer']
            sa_hash = bcrypt.hashpw(secret_a.encode(), bcrypt.gensalt()).decode()
            user_to_update.first_name = request.POST["first_name"]
            user_to_update.last_name = request.POST["last_name"]
            user_to_update.email = request.POST["email"]
            user_to_update.dob = request.POST["dob"]
            user_to_update.password = pw_hash
            user_to_update.secret_question = request.POST['secret_question']
            user_to_update.secret_answer = sa_hash
            user_to_update.save()
        return redirect(f'/account/{id}')

# -------------------------------------------- DASHBOARD
def dashboard(request):
    user = User.objects.get(id=request.session['id'])
    future_events = user.attendees.all()
    events_attending_but_not_organized = []
    for event in future_events:
        if event.user != user:
            events_attending_but_not_organized.append(event)
    context = {
        'one_user' : user,
        'user_events' : Event.objects.filter(user = User.objects.get(id=request.session['id'])),
        'todays_date' : todays_date.strftime("%A, %b %d"),
        'future_events' : events_attending_but_not_organized,
    }
    return render(request, "dashboard.html", context)

# -------------------------------------------- CREATE & DELETE EVENTS
def create_event_page(request):
    return render(request, "create_event.html")

def create_event(request):
    if request.method == "POST":
        errors = Event.objects.event_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/create/event')
        else:
            event = Event.objects.create(title = request.POST["title"].title(), date=request.POST["date"], time=request.POST['time'], max_attendees=request.POST['max_attendees'], information=request.POST['information'], location=request.POST['location'].title(), user = User.objects.get(id=request.session['id']), number_of_attendees=0)
            return redirect(f'join/{event.id}')
    return redirect('/dashboard')

def cancel_event(request, id):
    user = User.objects.get(id=request.session['id'])
    event = Event.objects.get(id=id)
    event.delete()
    return redirect('/dashboard')

# -------------------------------------------- VIEW EVENTS & JOIN/UNJOIN
def view_event(request, id):
    event = Event.objects.get(id=id)
    attendees = event.attendees.all()
    # figuring out which button to show, join or unjoin
    user_attends = False
    # figuring out if need to show event is full
    event_full = False
    attendee_list = []
    # counting attendees
    for attendee in attendees:
        attendee_list.append(attendee.first_name)
        if request.session['id'] == attendee.id:
            user_attends = True
    if event.number_of_attendees == event.max_attendees:
        event_full = True
    open_spots = event.max_attendees - event.number_of_attendees
    
    all_messages = Message.objects.filter(event=event)

    # trying not to have a trailing comma after last attendee (happens when doing a loop in HTML)
    attendee_list = ', '.join(attendee_list)
    
    context = {
        "event" : event,
        "attendees" : attendees,
        "attendee_list" : attendee_list,
        "user_attends" : user_attends,
        "event_full" : event_full,
        "open_spots" : open_spots,
        "all_messages" : all_messages,
        "user" : User.objects.get(id=request.session['id'])
    }
    return render(request, 'view_event.html', context)

def join_event(request, id):
    user = User.objects.get(id=request.session['id'])
    event = Event.objects.get(id=id)
    event.attendees.add(user)
    event.number_of_attendees += 1
    event.save()
    return redirect('/dashboard')

def unjoin_event(request, id):
    user = User.objects.get(id=request.session['id'])
    event = Event.objects.get(id=id)
    event.attendees.remove(user)
    event.number_of_attendees -= 1
    event.save()
    return redirect('/dashboard')

# -------------------------------------------- MESSAGES IN EVENTS (CREATE/DELETE/EDIT)
def create_message(request,id):
    if request.method == "POST":
        errors = Message.objects.message_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect(f'/view_event/{id}')
        else:
            Message.objects.create(content = request.POST["content"], user = User.objects.get(id=request.session['id']), event = Event.objects.get(id=id))
        return redirect(f'/view_event/{id}')

def delete_message(request, id, ide):
    message_to_delete = Message.objects.get(id=id)
    message_to_delete.delete()
    return redirect(f'/view_event/{ide}')

def edit_message(request, id, ide):
    event = Event.objects.get(id=ide)
    attendees = event.attendees.all()
    # figuring out which button to show, join or unjoin
    user_attends = False
    # figuring out if need to show event is full
    event_full = False
    # counting attendees
    for attendee in attendees:
        if request.session['id'] == attendee.id:
            user_attends = True
    if event.number_of_attendees == event.max_attendees:
        event_full = True
    open_spots = event.max_attendees - event.number_of_attendees
    
    all_messages = Message.objects.filter(event=event)
    edit = True

    context = {
        "event" : event,
        "attendees" : attendees,
        "user_attends" : user_attends,
        "event_full" : event_full,
        "open_spots" : open_spots,
        "all_messages" : all_messages,
        "user" : User.objects.get(id=request.session['id']),
        "editing_message" : Message.objects.get(id=id),
        "edit" : edit
    }
    return render(request, 'view_event.html', context)

def message_edited(request, id, ide):
    if request.method == "POST":
        errors = Message.objects.message_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request,value)
            return redirect(f'/view_event/{ide}')
        else:
            message = Message.objects.get(id=id)
            message.content = request.POST['content']
            message.save()
    return redirect(f'/view_event/{ide}')

# -------------------------------------------- SEARCH
def search(request):
    context = {
        "all_events" : Event.objects.exclude(user=User.objects.get(id=request.session['id']))
    }
    return render(request, 'search.html', context)

def target_search(request):
    search = request.GET['search']
    filtered_events = Event.objects.filter(title__icontains=search)
    context = {
        "filtered_events" : filtered_events
    }
    return render(request, 'search.html', context)
    
# @app.route('/run_weather', methods = ['POST'])
# def run_weather():
#     the_call = requests.get(f"https://api.openweathermap.org/data/2.5/weather?zip={request.form['zipcode']}&appid=c36d1fbf846390b701c5c9f6937564e8&units=imperial").json()
#     # pprint.pprint(the_call.json())
#     # print("City",the_call['name'])
#     #need to create a session
#     session['city'] = the_call['name']
#     session['humidity'] = the_call['main']['humidity']
#     session['wind'] = the_call['wind']['speed']
#     session['temp'] = the_call['main']['temp']
#     session['description'] = the_call['weather'][0]['description']
#     # print("Description", the_call['weather'][0]['description'])
#     return redirect('/dashboard')

# Date and weather API input
#             <form action="/run_weather" method="POST">
#                 <label for="">ZIPCODE</label>
#                 <input type="text" name="zipcode">
#                 <button>Submit</button>
#             </form>
#             <h2>Current Weather Conditions:</h2>
#             <h3>City: {{session.city}}</h3>
#             <h3>Temperature: {{session.temp}} Degrees</h3>
#             <h3>Wind: {{session.wind}} MPH</h3>
#             <h3>Humidity: {{session.humidity}} %</h3>
#             <h3>Description: {{session.description}}</h3>

#   https://www.google.com/maps/embed/v1/MAP_MODE?key=YOUR_API_KEY&parameters
