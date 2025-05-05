from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.core.mail import send_mail

import random

active_rooms = {}  # Global dictionary to keep track of active rooms and their participant counts

def features(request):
    return render(request, 'features.html')
from django.http import JsonResponse

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Construct the email content
        subject = f"New Contact Message from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            # Send the email
            send_mail(
                subject,
                body,
                'your_email@gmail.com',  # Replace with your email
                ['chakravarthy.atipamula@gmail.com'],  # Replace with the recipient email
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to send message. Please try again.'})
    
    return render(request, 'contact.html')


def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return render(request, 'login.html', {'success': "Registration successful. Please login."})
            except IntegrityError:
                error_message = "A user with that username already exists."
                return render(request, 'register.html', {'error': error_message, 'form': form})
        else:
            error_message = form.errors.as_text()
            return render(request, 'register.html', {'error': error_message, 'form': form})

    return render(request, 'register.html', {'form': RegisterForm()})

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return render(request, 'login.html', {'error': "Invalid credentials. Please try again."})

    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'name': request.user.first_name})

@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.first_name + " " + request.user.last_name})

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login")

@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        return redirect("/meeting?roomID=" + roomID)
    return render(request, 'joinroom.html')

@login_required
def random_call(request):
    global active_rooms

    # Find a room with less than 2 participants
    roomID = None
    for room, count in active_rooms.items():
        if count < 2:
            roomID = room
            active_rooms[room] += 1
            break

    if roomID is None:
        # Create a new room if no room with less than 2 participants is found
        roomID = str(random.randint(1000, 9999))
        active_rooms[roomID] = 1
    else:
        # Remove the room from active_rooms if it reaches 2 participants
        if active_rooms[roomID] >= 2:
            del active_rooms[roomID]
    
    return redirect("/meeting?roomID=" + roomID)

# Django views.py (e.g., in a video_app/views.py)
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import os


@api_view(['POST'])
@parser_classes([MultiPartParser])
def save_recording(request):
  if request.method == 'POST' and request.FILES.get('file'):
      recording_file = request.FILES['file']

      # Define the upload directory based on your setup
      upload_dir = 'media/recordings'  
      os.makedirs(upload_dir, exist_ok=True) # Make sure the dir exist

      file_path = os.path.join(upload_dir, recording_file.name)
      
      with open(file_path, 'wb+') as destination:
           for chunk in recording_file.chunks():
              destination.write(chunk)
          
      return Response({'message': 'Recording saved successfully'}, status=200)
      
  return Response({'error': 'File missing or incorrect method'}, status=400)