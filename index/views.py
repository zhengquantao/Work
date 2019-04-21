from django.shortcuts import render


def index(request):

    print("123456")
    return render(request, 'index.html')
