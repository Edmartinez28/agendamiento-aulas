from django.shortcuts import render

# Create your views here.
def inventariototal(request):
    return render(request, "inventario.html")
