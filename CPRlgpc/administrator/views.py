from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes
from account.models import CustomUser
from account.forms import CustomUserForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json  # Not used

import math as m
import random as r
from django_renderpdf.views import PDFView

import numpy as np
import pandas as pd
import csv
from io import TextIOWrapper


def find_n_winners(data, n):
    """Read More
    https://www.geeksforgeeks.org/python-program-to-find-n-largest-elements-from-a-list/
    """
    final_list = []
    candidate_data = data[:]
    # print("Candidate = ", str(candidate_data))
    for i in range(0, n):
        max1 = 0
        if len(candidate_data) == 0:
            continue
        this_winner = max(candidate_data, key=lambda x: x['votes'])
        # TODO: Check if None
        this = this_winner['name'] + \
            " with " + str(this_winner['votes']) + " votes"
        final_list.append(this)
        candidate_data.remove(this_winner)
    return ", &nbsp;".join(final_list)


class PrintView(PDFView):
    template_name = 'admin/print.html'
    prompt_download = True

    @property
    def download_name(self):
        return "result.pdf"

    def get_context_data(self, *args, **kwargs):
        title = "E-voting"
        try:
            file = open(settings.ELECTION_TITLE_PATH, 'r')
            title = file.read()
        except:
            pass
        context = super().get_context_data(*args, **kwargs)
        position_data = {}

        LGUDTData = []
        for position2 in Position.objects.all().order_by('priority'):
            
            LGUDT = {}
            LGUPOS = ""
            if position2.cat == "LGU":
                for lgu in LGU.objects.all():
                    LGUDT = {}
                    LGUPOS = position2.name + " for " + lgu.name
                    LGUDT['name'] = LGUPOS
                    LGUDT['lguname'] = lgu.name
                    LGUDT['positionname'] = position2.id
                    LGUDT['max_vote'] = position2.max_vote
                    LGUDTData.append(LGUDT)                
                  
                    # print("lgu for  ", str(LGUDT))
            else:
                LGUDT = {}
                LGUPOS = position2.name
                LGUDT['name'] = LGUPOS
                LGUDT['lguname'] = "National"
                LGUDT['positionname'] = position2.id
                LGUDT['max_vote'] = position2.max_vote
                LGUDTData.append(LGUDT)
                # print("lgu for  ", str(LGUDT))
            # for lgu in LGU.objects.all():
            #     if position2.cat == "LGU":
            #         LGUPOS = position2.name + " " + lgu.name
            #     else:
            #         LGUPOS = position2.name
            #     LGUDT['name'] = LGUPOS
            #     LGUDT['positionname'] = position2.id
            #     LGUDT['max_vote'] = position2.max_vote
            #     LGUDTData.append(LGUDT)
                
            # print("lgu for  ", str(LGUDT))
            # print(LGUDTData)
        # print(LGUDTData)
        for id, position in enumerate(LGUDTData):
            
            candidate_data = []
            winner = ""
            if position["lguname"] == "National":
                for candidate in Candidate.objects.filter(position=position["positionname"]):
                    this_candidate_data = {}               
                    votes = Votes.objects.filter(candidate=candidate).count()
                    this_candidate_data['name'] = candidate.fullname
                    this_candidate_data['votes'] = votes
                    candidate_data.append(this_candidate_data)
            else:
                for candidate in Candidate.objects.filter(position=position["positionname"]):
                    this_candidate_data = {}    
                    if candidate.lgu.name ==  position["lguname"]:        
                        votes = Votes.objects.filter(candidate=candidate).count()
                        this_candidate_data['name'] = candidate.fullname
                        this_candidate_data['votes'] = votes
                        candidate_data.append(this_candidate_data)
                
                
                
            # for candidate in Candidate.objects.filter(position=position["positionname"]):
            #     this_candidate_data = {}               
            #     votes = Votes.objects.filter(candidate=candidate).count()
            #     this_candidate_data['name'] = candidate.fullname
            #     this_candidate_data['votes'] = votes
            #     candidate_data.append(this_candidate_data)
                
                
               
            # print("Candidate1 Data For  ", str(
            #     position["name"]), " = ", str(this_candidate_data))
            # ! Check Winner
            if len(candidate_data) < 1:
                winner = "Position does not have candidates"
            else:
                # Check if max_vote is more than 1
                if position["max_vote"] > 1:
                    winner = find_n_winners(candidate_data, position["max_vote"])
                else:

                    winner = max(candidate_data, key=lambda x: x['votes'])
                    if winner['votes'] == 0:
                        winner = "No one voted for this yet position, yet."
                    else:
                        """
                        https://stackoverflow.com/questions/18940540/how-can-i-count-the-occurrences-of-an-item-in-a-list-of-dictionaries
                        """
                        count = sum(1 for d in candidate_data if d.get(
                            'votes') == winner['votes'])
                        if count > 1:
                            winner = f"There are {count} candidates with {winner['votes']} votes"
                        else:
                            winner = "Winner : " + winner['name']
            # print("Candidate Data For  ", str(
            #     position["name"]), " = ", str(candidate_data))
            position_data[position["name"]] = {
                'candidate_data': candidate_data, 'winner': winner, 'max_vote': position["max_vote"]}
        context['positions'] = position_data
        # print(context)
        return context




def dashboard(request):
    LGUDTData = []
    counter = 1  # Initialize a counter variable

    for position2 in Position.objects.all().order_by('priority'):
        LGUDT = {}
        LGUPOS = ""

        if position2.cat == "LGU":
            for lgu in LGU.objects.all():
                LGUDT = {}
                LGUPOS = position2.name + " for " + lgu.name
                LGUDT['id'] = counter  # Add the id column
                LGUDT['name'] = LGUPOS
                LGUDT['lguname'] = lgu.name
                LGUDT['positionname'] = position2.id
                LGUDT['max_vote'] = position2.max_vote
                LGUDTData.append(LGUDT)
                counter += 1  # Increment the counter
        else:
            LGUDT = {}
            LGUPOS = position2.name
            LGUDT['id'] = counter  # Add the id column
            LGUDT['name'] = LGUPOS
            LGUDT['lguname'] = "National"
           
            LGUDT['positionname'] = position2.id
            LGUDT['max_vote'] = position2.max_vote
            LGUDTData.append(LGUDT)
            counter += 1  # Increment the counter
    
    
    
    positions = LGUDTData
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    chart_data = {}

    for position in positions:
        list_of_candidates = []
        votes_count = []
        
        if position["lguname"] == "National":
            for candidate in Candidate.objects.filter(position=position['positionname']):
                    list_of_candidates.append(candidate.fullname)
                    votes = Votes.objects.filter(candidate=candidate).count()
                    votes_count.append(votes)
            chart_data[position['name']] = {
            'candidates': list_of_candidates,
            'votes': votes_count,
            'pos_id': position['positionname']
            }
        else:
            for candidate in Candidate.objects.filter(position=position['positionname']):
                if candidate.lgu.name == position['lguname']:
                        list_of_candidates.append(candidate.fullname)
                        votes = Votes.objects.filter(candidate=candidate).count()
                        votes_count.append(votes)
                chart_data[position['name']] = {
                'candidates': list_of_candidates,
                'votes': votes_count,
                'pos_id': position['positionname']
                }
        
        
       
        # for candidate in Candidate.objects.filter(position=position['positionname']):
        #     list_of_candidates.append(candidate.fullname)
        #     votes = Votes.objects.filter(candidate=candidate).count()
        #     votes_count.append(votes)
        # chart_data[position['name']] = {
        #     'candidates': list_of_candidates,
        #     'votes': votes_count,
        #     'pos_id': position['id']
        # }
    # print(chart_data)
    
    
    
    
    
    
    context = {
        'position_count': len(positions),
        'candidate_count': candidates.count(),
        'voters_count': voters.count(),
        'voted_voters_count': voted_voters.count(),
        'positions': positions,
        'chart_data': chart_data,
        'page_title': "Dashboard"
    }
    return render(request, "admin/home.html", context)



# def voters(request):
#     voters = Voter.objects.all()
#     userForm = CustomUserForm(request.POST or None)
#     voterForm = VoterForm(request.POST or None)
#     context = {
#         'form1': userForm,
#         'form2': voterForm,
#         'voters': voters,
#         'page_title': 'Voters List'
#     }
#     if request.method == 'POST':
#         if userForm.is_valid() and voterForm.is_valid():
            
            
#             user = userForm.save(commit=False)
           
#             voter = voterForm.save(commit=False)
#             voter.admin = user
#             user.save()
#             voter.save()
#             messages.success(request, "New voter created")
#         else:
#             messages.error(request, "Form validation failed")
#     return render(request, "admin/voters.html", context)


def voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List'
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            
            
            user = userForm.save(commit=False)
           
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/voters.html", context)



def votersBY(request,lgu_id):
    
    if lgu_id == "":
        voters = Voter.objects.all()
    else:
        voters = Voter.objects.filter(lgu_id=lgu_id)
    lguname = LGU.objects.filter(id=lgu_id).values_list('name', flat=True).first()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'lguname': lguname,
        'page_title': 'Voters List'
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            
            
            user = userForm.save(commit=False)
           
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/voters.html", context)

# def bulk_create_voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(prefix='user')
    voterForm = VoterForm(prefix='voter')
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List'
    }
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if the uploaded file is a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a CSV file")
            return redirect('adminViewVoters')
        
        # Parse the CSV file and create voter objects
        try:
            voters_to_create = []
            csv_text = TextIOWrapper(csv_file.file, encoding='utf-8-sig')
            reader = csv.DictReader(csv_text)
           
            for row in reader:
                username = row['LASTNAME'] + row['FIRSTNAME']
                password = row['STUDENTNO']
                # print(username)
                # print(password)
                # Assuming you have defined user_form and voter_form
                if userForm.is_valid() and voterForm.is_valid():
                    user = userForm.save()
                    voter = voterForm.save(commit=False)
                    voter.admin = user
                    voters_to_create.append(voter)
                else:
                    messages.error(request, "Form validation failed for a row in the CSV")
                    return redirect('adminViewVoters')
            
            # Bulk create the voter objects
            Voter.objects.bulk_create(voters_to_create)
            
            messages.success(request, "New voters created from CSV")
            return redirect('adminViewVoters')
        except UnicodeDecodeError as e:
            messages.error(request, f"Error decoding CSV file: {e}. Try using a different encoding.")
            return redirect('adminViewVoters')
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {e}")
            return redirect('adminViewVoters')
    

    return render(request, 'admin/bulk_create_voters.html')

def create_voter(user_data, voter_data):
    user = CustomUserForm(user_data).save(commit=False)
    user.save()
    
     # Define a dynamic form class with the additional field
    class DynamicVoterForm(VoterForm):
        otp = forms.CharField()  # Define the additional field here

        class Meta(VoterForm.Meta):
            fields = VoterForm.Meta.fields + ['otp'] 
    
    voter_form_data = voter_data.copy()
    
    
    # voter = VoterForn(voter_data).save(commit=False)
    voter = DynamicVoterForm(voter_form_data).save(commit=False)
    voter.admin = user
    voter.save()
    

def bulk_create_voters(request):
    
    
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List'
    }
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
        else:
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    lgu_name = row['COLLEGE'].strip()  # Assuming 'LGU' is the column name for LGU name
                    try:
                        
                        lgu = LGU.objects.get(description=lgu_name)  # Query the LGU based on name
                    except LGU.DoesNotExist:
                        messages.error(request, f'LGU with description "{lgu_name}" not found')
                        continue
                    
                    try:
                        student_no = str(row['STUDENTNO']).strip().lower()
                    except KeyError:
                        messages.error(request, 'STUDENTNO field is missing in the CSV file')
                        continue  # Move to the next row
                    # print(student_no)
                    fullname = row['FIRSTNAME'].strip().lower() +" "+ row['LASTNAME'].strip().lower()
                    OTP = genotp()
                    
                    
                    user_data = {
                        'username': student_no,  # Compose username,
                        'password': OTP,
                        'last_name': row['LASTNAME'].strip(),
                        'first_name': row['FIRSTNAME'].strip(),
                        'email' : "",
                    }
                    print(user_data)
                   
                    voter_data = {
                        'lgu': lgu.id,  
                        'otp' : OTP,                   
                        'phone': "0",
                    }
                    # print(voter_data)
                    userForm = CustomUserForm(user_data)
                    if userForm.is_valid():
                        create_voter(user_data, voter_data)
                    else:                        
                        
                        messages.error(request, f'User creation failed: {userForm.errors.as_text()}')
                messages.success(request, 'Voters created successfully')
            except Exception as e:
                
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        messages.error(request, 'Please upload a CSV file')
    return render(request, "admin/voters.html", context)



def view_voter_by_id(request):
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['first_name'] = voter.admin.first_name
        context['last_name'] = voter.admin.last_name
        context['phone'] = voter.phone
        context['id'] = voter.id
        context['username'] = voter.admin.username
        context['email'] = voter.admin.email
        context['password'] = voter.admin.password
        #
        #context['lgu'] =  voter.lgu
        previous = VoterForm(instance=voter)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def view_position_by_id(request):
    pos_id = request.GET.get('id', None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        pos = pos[0]
        context['name'] = pos.name
        context['max_vote'] = pos.max_vote
        context['id'] = pos.id
        context['cat'] = pos.cat
        previous = PositionForm(instance=pos)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def updateVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Voter.objects.get(id=request.POST.get('id'))
        user = CustomUserForm(request.POST or None, instance=instance.admin)
        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Voter's bio updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))























def deleteVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Voter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def passVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Voter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))

def viewPositions(request):
    positions = Position.objects.order_by('-priority').all()
    form = PositionForm(request.POST or None)
    context = {
        'positions': positions,
        'form1': form,
        'page_title': "Positions"
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1  # Just in case it is empty.
            form.save()
            messages.success(request, "New Position Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Position.objects.get(id=request.POST.get('id'))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        messages.success(request, "Position has been updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))






def deletePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Position.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Position Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))


def viewCandidates(request):
    candidates = Candidate.objects.all()
    form = CandidateForm(request.POST or None, request.FILES or None)
    context = {
        'candidates': candidates,
        'form1': form,
        'page_title': 'Candidates'
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save()
            messages.success(request, "New Candidate Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/candidates.html", context)


def updateCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        form = CandidateForm(request.POST or None,
                             request.FILES or None, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate Data Updated")
        else:
            messages.error(request, "Form has errors")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def deleteCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Candidate.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Candidate Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates'))


def view_candidate_by_id(request):
    candidate_id = request.GET.get('id', None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context['code'] = 404
    else:
        candidate = candidate[0]
        context['code'] = 200
        context['fullname'] = candidate.fullname

        previous = CandidateForm(instance=candidate)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def ballot_position(request):
    context = {
        'page_title': "Ballot Position"
    }
    return render(request, "admin/ballot_position.html", context)


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {
            'error': False
        }
        position = Position.objects.get(id=position_id)
        if up_or_down == 'up':
            priority = position.priority - 1
            if priority == 0:
                context['error'] = True
                output = "This position is already at the top"
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority+1))
                position.priority = priority
                position.save()
                output = "Moved Up"
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "This position is already at the bottom"
                context['error'] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority-1))
                position.priority = priority
                position.save()
                output = "Moved Down"
        context['message'] = output
    except Exception as e:
        context['message'] = e

    return JsonResponse(context)


def ballot_title(request):
    from urllib.parse import urlparse
    url = urlparse(request.META['HTTP_REFERER']).path
    from django.urls import resolve
    try:
        redirect_url = resolve(url)
        title = request.POST.get('title', 'No Name')
        file = open(settings.ELECTION_TITLE_PATH, 'w')
        file.write(title)
        file.close()
        messages.success(
            request, "Election title has been changed to " + str(title))
        return redirect(url)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


def viewVotes(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Votes'
    }
    return render(request, "admin/votes.html", context)


def resetVote(request):
    Votes.objects.all().delete()
    Voter.objects.all().update(voted=False, verified=True)
    messages.success(request, "All votes has been reset")
    return redirect(reverse('viewVotes'))





def OTPgen(request) : 
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
  
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['id'] = voter.id
        OTP = ""      
           
        if  voter.otp is None or voter.otp=="":
        #   OTP = genotp()
            3
        else:
            OTP = voter.otp
        context['otp'] = OTP
        
        
                       
        
    # Declare a string variable   
    # which stores all alpha-numeric characters    
    
    return JsonResponse(context)

def genotp():
    OTP = ""
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    varlen = len(string)
    for i in range(6):
        OTP += string[m.floor(r.random() * varlen)]
    return OTP


def OTPsave(request) : 
        
        
        
        if request.method == 'POST':
            OTP= request.POST.get('otp')
            voterid = request.POST.get('id')
            #voter.verified = True
           #voter.save(update_fields=['otp'])
            Voter.objects.filter(id=voterid).update(otp=OTP)
        return redirect(reverse('adminViewVoters'))
                
        
    # Declare a string variable   
    # which stores all alpha-numeric characters    
    
def viewvotePositions(request,position_id,lgu_id):
    
    positions = Position.objects.all().order_by('priority')
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    
      
    try:
        pos = Position.objects.get(id=position_id)
        poscat = pos.cat
    except LGU.DoesNotExist:
    # Handle the case where the LGU with the specified ID does not exist
        poscat = None  # or any default value you want to assign
    
    
    try:
        lgu = LGU.objects.get(name=lgu_id)
        lguid = lgu.id
    except LGU.DoesNotExist:
    # Handle the case where the LGU with the specified ID does not exist
        lguid = None  # or any default value you want to assign
    
    print(lguid)
    if poscat == "National":
        chart_data = {}   

        for candidate in Candidate.objects.filter(position=position_id):
            votes_count = 0
            print(candidate)
            for lgu in LGU.objects.all():
                votes_count = Votes.objects.all().select_related('voter','voter__lgu').filter(voter__lgu__name=lgu,candidate__fullname=candidate).count()
                        
                #list_of_candidates.append(candidate.fullname)
                #votes = Votes.objects.filter(candidate=candidate).count()
                #votes_count.append(votes)
                #votes_count = votes
                chart_data = {
                'candidates': candidate.fullname,
                'votes': votes_count, 
                'lgu': lgu.name,  
                        
                }
                list_of_candidates.append(chart_data)
            # print(list_of_candidates)
            data = pd.DataFrame.from_dict(list_of_candidates)
            # Convert 'votes' column from string to integer
            data['votes'] = data['votes'].astype(int)            
            data = pd.pivot_table(data,index='candidates', columns='lgu', values='votes', aggfunc='sum')
            # Adding a total amount column
            data['Total'] = data.sum(axis=1)                          
            data.reset_index(inplace=True)
            
            
            
    
    
    else:
    
    
        chart_data = {}   

        for candidate in Candidate.objects.filter(position=position_id,lgu=lguid):
            votes_count = 0
                       
            votes_count = Votes.objects.all().select_related('voter','voter__lgu').filter(voter__lgu__name=lgu,candidate__fullname=candidate).count()
                        
                #list_of_candidates.append(candidate.fullname)
                #votes = Votes.objects.filter(candidate=candidate).count()
                #votes_count.append(votes)
                #votes_count = votes
            chart_data = {
                'Candidates': candidate.fullname,
                'votes': votes_count, 
                  
                        
                }
            list_of_candidates.append(chart_data)
            # print(list_of_candidates)
            data = pd.DataFrame.from_dict(list_of_candidates)
            # Convert 'votes' column from string to integer
            data['votes'] = data['votes'].astype(int)            
            # data = pd.pivot_table(data,index='candidates', columns='lgu', values='votes', aggfunc='sum')
            # # Adding a total amount column
            # data['Total'] = data.sum(axis=1)                          
            # data.reset_index(inplace=True)
    
    pivot_tables = []
    # for candidate in Candidate.objects.filter(position=position_id):
    #     votes_count = 0
    #     chart_data = []
    #     for lgu in LGU.objects.all():
    #         votes_count = Votes.objects.all().select_related('voter','voter__lgu').filter(voter__lgu__name=lgu,candidate__fullname=candidate).count()
            
    #         chart_data = {
    #          'candidates': candidate.fullname,
    #          'votes': votes_count, 
    #          'lgu': lgu.name,  
                      
    #         }
    #         list_of_candidates.append(chart_data)
            
          

    #     data = pd.DataFrame.from_dict(list_of_candidates)
    #     data['votes'] = data['votes'].astype(int)            
    #     data = pd.pivot_table(data,index='candidates', columns='lgu', values='votes', aggfunc='sum')
        
    #     data['Total'] = data.sum(axis=1)                          
    #     data.reset_index(inplace=True)
    #     pivot_tables.append((candidate.fullname, data))
        
        
        
    PositionName = Position.objects.filter(id=position_id).values_list('name', flat=True).first()   
    context = {
        'table1': data,
        'PosName': PositionName,
        'page_title': "Dashboard"
    }
    
    
    return render(request, "admin/votestally.html", context)
                  
                
                
                #votes = Votes.objects.filter(candidate=candidate).count()
                # this_candidate_data['name'] = candidate.fullname
                
                # this_candidate_data['votes'] = votes
                # candidate_data.append(this_candidate_data)
    
    
    
    #return redirect(reverse('adminDashboard'))

   

def viewLgus(request):
    lgus = LGU.objects.order_by('-priority').all()
    form = LGUForm(request.POST or None)
    context = {
        'lgus': lgus,
        'form1': form,
        'page_title': "LGU"
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = lgus.count() + 1  # Just in case it is empty.
            form.save()
            messages.success(request, "New lgus Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/lgus.html", context)
 
 

def viewLgus_by_id(request):
    lgus_id = request.GET.get('id', None)
    lgus = LGU.objects.filter(id=lgus_id)
    context = {}
    if not lgus.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        lgus = lgus[0]
        context['name'] = lgus.name
        context['description'] = lgus.description
        context['id'] = lgus.id
        
        previous = LGUForm(instance=lgus)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)

def updateLGU(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = LGU.objects.get(id=request.POST.get('id'))
        lgu = LGUForm(request.POST or None, instance=instance)
        lgu.save()
        messages.success(request, "Position has been updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewLgus'))




def deleteLGU(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        lgu = LGU.objects.get(id=request.POST.get('id'))
        lgu.delete()
        messages.success(request, "Position Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewLgus'))


class PrintView(PDFView):
    template_name = 'admin/print.html'
    prompt_download = True

    @property
    def download_name(self):
        return "result.pdf"

    def get_context_data(self, *args, **kwargs):
        title = "E-voting"
        try:
            file = open(settings.ELECTION_TITLE_PATH, 'r')
            title = file.read()
        except:
            pass
        context = super().get_context_data(*args, **kwargs)
        
        
        
        return context