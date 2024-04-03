from django.db import models
from account.models import CustomUser
# Create your models here.

class LGU(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name
    
class Voter(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11)  # Used for OTP
    otp = models.CharField(max_length=10, null=True)
    verified = models.BooleanField(default=False)
    voted = models.BooleanField(default=False)
    otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent
    lgu = models.ForeignKey(LGU, on_delete=models.CASCADE)
    timevoted = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


Cat_CHOICES = (
    ('National','National'),
    ('LGU', 'LGU'),
  
)

class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()
    cat = models.CharField(max_length=10, choices=Cat_CHOICES)
     
    def __str__(self):
        return self.name



class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    lgu = models.ForeignKey(LGU, on_delete=models.CASCADE,default='SOME STRING')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
   
    
    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
