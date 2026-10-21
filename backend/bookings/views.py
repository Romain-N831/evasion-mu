from django.shortcuts import render

def index(request):
    
    context = {
        'page_title' : 'Bookings',
    }
    return render(request, 'bookings/home.html', context)

# Create your views here.
