from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')
    fName = forms.CharField(max_length=100, required=True, label='First Name')
    lName = forms.CharField(max_length=100, required=True, label='Last Name')

    class Meta:
        model = User
        fields = ("email", "fName", "lName", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["fName"]
        user.last_name = self.cleaned_data["lName"]

        if commit:
            user.save()
        return user

class ProgramChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
class SubscriptionForm(forms.Form):
    tier1_price = TierText.objects.get(tier=1).tier_price
    tier2_price = TierText.objects.get(tier=2).tier_price
    tier3_price = TierText.objects.get(tier=3).tier_price
    subscription_options = [
        ('Tier 1', 'Tier 1 Subscription ($' + str(tier1_price) + ' USD/Mon)'),
        ('Tier 2', 'Tier 2 Subscription ($' + str(tier2_price) + ' USD/Mon)'),
        ('Tier 3', 'Tier 3 Subscription ($' + str(tier3_price) + ' USD/Mon)'),
    ]
    plans = forms.ChoiceField(choices=subscription_options)

class AddVideo(forms.Form):
    video_link = forms.CharField(max_length=100, required=True, label='Video Link')
    name = forms.CharField(max_length=100, required=True, label='Video Name')
    description = forms.CharField(max_length=100, required=False, label='Video Description')

class VideoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
class DeleteVideo(forms.Form):
    video_to_delete = VideoChoiceField(queryset=Video.objects.all())

class CreateProgram(forms.Form):
    program_name = forms.CharField(max_length=100, required=True, label='Program Name')
    description = forms.CharField(max_length=100, required=False, label='Program Description')

class DeleteProgram(forms.Form):
    program_to_delete = ProgramChoiceField(queryset=Program.objects.all())
    
class AssignProgramForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    program = ProgramChoiceField(queryset=Program.objects.all())
    start_date = forms.DateField(label='Start Date', input_formats=['%m/%d/%Y'],widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))
    repeats = forms.IntegerField(label = 'Number of weeks to repeat (type 0 to assign for a year(55 weeks))')

    class Meta:
        model = UPJunction
        fields = ('user', 'program', 'start_date', 'repeats')

class UnassignProgramForm(forms.Form):
    user_unassign = forms.ModelChoiceField(queryset=User.objects.all())
    programToUnassign = ProgramChoiceField(queryset=Program.objects.all(), label='Program')

class AssignVideoForm(forms.ModelForm):
    program = ProgramChoiceField(queryset=Program.objects.all())
    video = VideoChoiceField(queryset=Video.objects.all())

    class Meta:
        model = PVJunction
        fields = ('program', 'video')

class CompleteProgramForm(forms.Form):
    complete  = forms.BooleanField(label='Complete', required=False)

class TrialCodeForm(forms.Form):
    code = forms.CharField(max_length=100, label='Trial Code')

class HomePageTextForm(forms.ModelForm):
    home_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 30}))
    class Meta:
        model = HomePageText
        fields = ['home_text']

class TierTextForm(forms.ModelForm):
    tier = forms.IntegerField()
    tier_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 30}))
    tier_price = forms.IntegerField()
    class Meta:
        model = TierText
        fields = ['tier', 'tier_text', 'tier_price']


