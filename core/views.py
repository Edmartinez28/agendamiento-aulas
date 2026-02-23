from django.shortcuts import render
from django.shortcuts import redirect

def error_404(request, exception):
    return redirect('home')   # 👈 nombre de tu url principal