from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm, Voter
from django.contrib.auth import login, logout
from django.utils import timezone
# Create your views here.


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = EmailBackend.authenticate(request, username=username, password=password)
        if user is not None:
            if user.user_type == '1':
                login(request, user)
                return redirect(reverse("adminDashboard"))
            else:
                try:
                    voting_status = Voter.objects.get(admin_id=user)
                    if voting_status.voted == 1:
                        # Check if 30 minutes have passed since voting
                        time_since_vote = timezone.now() - voting_status.timevoted
                        print(timezone.now())
                        print(voting_status.timevoted)
                        print(time_since_vote)
                        if time_since_vote.total_seconds() > 30 * 60:
                            messages.error(request, "Your account is disabled due to voting.")
                            return redirect(reverse("account_login"))
                        else:
                            login(request, user)                                   
                            return redirect(reverse("voterDashboard"))
                    else:
                        login(request, user)
                        
                     
                        return redirect(reverse("voterDashboard"))
                except Voter.DoesNotExist:
                    messages.error(request, "Voting status not found.")
                    return redirect(reverse("account_login"))
        else:
            messages.error(request, "Invalid username or password")
            return redirect(reverse("account_login"))

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))
