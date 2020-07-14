from django.shortcuts import render, redirect

from .forms import UserSignupForm


def signup(request):
    form = UserSignupForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        return redirect('accounts:login')

    return render(request, 'accounts/signup.html', {
        'form': form,
    })
