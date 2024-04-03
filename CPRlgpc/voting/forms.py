from django import forms
from .models import *
from account.forms import FormSettings


class VoterForm(FormSettings):
    class Meta:
        model = Voter
        fields = ['phone','lgu']
       


class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ['name', 'max_vote','cat']


class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = ['fullname', 'bio','lgu', 'position', 'photo']


class LGUForm(FormSettings):
    class Meta:
        model = LGU
        fields = ['name', 'description']