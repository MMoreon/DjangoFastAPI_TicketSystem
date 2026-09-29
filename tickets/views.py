from django.http import HttpResponse
# from django.shortcuts import render

# def auth(req):
#     return render(req, 'core/index.html')

def auth(req):
    return HttpResponse("Вход")

def home(req):
    return HttpResponse("Успешно пройдено")

def register(req):
    return HttpResponse("Регистрация")