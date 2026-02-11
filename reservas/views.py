from django.shortcuts import render

# Create your views here.

def reservaslaboratorios(request):
    return render(request, "reservaslaboratorios.html")