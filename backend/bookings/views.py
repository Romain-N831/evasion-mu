from django.shortcuts import render

def index(request):
    
    context = {
        'Page_Title' : 'Bookings',
    }
    return render(request, 'bookings/home.html', context)

# Create your views here.
