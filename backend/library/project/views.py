from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Book, Collection
from django.contrib.auth.models import User
from .forms import signupForm, loginForm
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view["GET"]
def home(request):
    query = request.GET.get("query")
    search_by = request.GET.get("search_by")

    if not query and not search_by:
                books = Book.objects.all()[:10]

    else:
        if search_by == 'title':
            books = Book.objects.filter(title__icontains=query)

        elif search_by == 'author':
            books = Book.objects.filter(author__icontains=query)

        elif search_by == 'isbn':
            books = Book.objects.filter(isbn__icontains=query)

    context = {
            'books':books,

        }
    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))


def userlogin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password =password)

            if user is not None:
                login(request, user)
                return redirect('/userdash/')

        message = 'Invalid Credentials'

        template = loader.get_template('login.html')

        return HttpResponse(template.render({'message': message}, request))

    form = loginForm()

    context = {
        'form': form,
    }

    template = loader.get_template('login.html')

    return HttpResponse(template.render(context, request))

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(username)

        if username and email and password:

            newUser= User.objects.create_user(
                username = username,
                email = email,
                password = password

            )

            newUser.save()

            # message = "Signup was successful"
            # template = loader.get_template('signup.html')
            return redirect('/login/')

    form = signupForm()

    context = {
        'form': form,
    }

    template = loader.get_template('signup.html')

    return HttpResponse(template.render(context, request))

def userdash(request):

    template= loader.get_template('dashbaord.html')

    return HttpResponse(template.render())

def book_details(request, id):

    book = Book.objects.filter(id=id)

    if book is not None:
        template = loader.get_template('bookdetail.html')

        context = {
            'book': book,
        }

        return HttpResponse(template.render(context,request))

    return HttpResponse("No Book found")


