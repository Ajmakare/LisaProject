import json
from django.http import HttpResponse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages 
import django_tables2 as tables
from .tables import *
from django.utils import timezone
from datetime import datetime, date
from django.contrib.auth.models import Group, User
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.utils.safestring import mark_safe
import calendar
from decouple import config
from django.http import QueryDict
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    template = "home.html"
    if request.user.is_authenticated:
        username = request.user.username
        user = User.objects.get(username=username)
        up_junctions = UPJunction.objects.filter(user=user)
        today = datetime.now().date()
        today_program = [up_junction.program for up_junction in up_junctions if up_junction.start_date == today]
        if today_program:
            today_program_name = today_program[0].name

            # Get the current date and set the date range for the month
            start_date = datetime.now().date()
            last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
            end_date = date(start_date.year, start_date.month, last_day_of_month)
            # Filter the UPJunction objects to only include the ones for the current user
            # and that have start dates in the date range
            up_junctions = UPJunction.objects.filter(user=request.user, start_date__range=(start_date, end_date))

            # Get the total number of programs the user has in the date range
            total_programs = up_junctions.count()

            # Get the number of completed programs in the date range
            completed_programs = up_junctions.filter(completed=True).count()

            # Calculate the percentage of completed programs
            if total_programs > 0:
                completion_percentage = (completed_programs / total_programs) * 100
            else:
                completion_percentage = 0
            home_text = HomePageText.objects.first()
            home_text = home_text.home_text

            return render(request, template, context={'today_program_name':today_program_name,'completion_percentage': completion_percentage, 'home_text': home_text})
        else:
            return render(request, template, context={'completion_percentage': 0})
    else:
        return render(request, template, context={})

@login_required
def profile(request):
        return render(request, 'profile.html', {})
    
@login_required
def all_programs(request):
    user = request.user
    upjunctions = UPJunction.objects.filter(user=user, completed=False).order_by('start_date')
    context = {'upjunctions': upjunctions}
    return render(request, 'all_programs.html', context)

@login_required
def controlPanel(request):
    videos = Video.objects.all()
    video_table = VideoTable(videos)

    program = Program.objects.all()
    program_table = ProgramTable(program)
    program_table.paginate(page=request.GET.get("page", 1), per_page=10)

    users = User.objects.all()
    user_table = UserTable(users)
    user_table.paginate(page=request.GET.get("page", 1), per_page=10)

    if request.user.is_authenticated and request.user.is_superuser:
        video_form = AddVideo(request.POST or None)
        delete_video_form = DeleteVideo(request.POST or None)
        program_form = CreateProgram(request.POST or None)
        delete_program_form = DeleteProgram(request.POST or None)
        assign_program_form = AssignProgramForm(request.POST or None)
        unassign_program_form = UnassignProgramForm(request.POST or None)
        unassign_video_form = UnassignVideoForm(request.POST or None)
        assign_video_form = AssignVideoForm(request.POST or None)
        home_text_form = HomePageTextForm(request.POST or None)
        tier_text_form = TierTextForm(request.POST or None)
        trial_code_form = TrialCodeForm(request.POST or None)
        if request.method == 'POST':
            if 'video_link' in request.POST:
                if video_form.is_valid():
                    link = video_form.cleaned_data['video_link']
                    name = video_form.cleaned_data['name']
                    description = video_form.cleaned_data['description']
                    video = Video(video_link=link, name=name, description=description)
                    video.save()
                    messages.success(request, 'Video added to database!')
                else:
                    print(assign_program_form.errors)
            elif 'video_to_delete' in request.POST:
                if delete_video_form.is_valid():
                    video = delete_video_form.cleaned_data['video_to_delete']
                    video.delete()
                    messages.success(request, 'Video Deleted!')
            elif 'program_name' in request.POST:
                if program_form.is_valid():
                    name = program_form.cleaned_data['program_name']
                    description = program_form.cleaned_data['description']
                    program = Program(name=name, description=description)
                    program.save()
                    messages.success(request, 'Program Created!')
            elif 'program_to_delete' in request.POST:
                if delete_program_form.is_valid():
                    program = delete_program_form.cleaned_data['program_to_delete']
                    program.delete()
                    messages.success(request, 'Program Deleted!')
            # Assign user program
            elif 'user' in request.POST:
                if assign_program_form.is_valid():
                    user = assign_program_form.cleaned_data['user']
                    program = assign_program_form.cleaned_data['program']
                    start_date = assign_program_form.cleaned_data['start_date']
                    repeats = assign_program_form.cleaned_data['repeats']
                    if repeats == 0:
                        repeats = 55
                        print(repeats)
                    for i in range(repeats):
                        UPJunction.objects.create(
                            user=user,
                            program=program,
                            start_date=start_date + timezone.timedelta(days=7 * i),
                            end_date=start_date + timezone.timedelta(days=7 * (i + 1)) - timezone.timedelta(days=1),
                        )
                    messages.success(request, 'Program Assigned!')
                else:
                    messages.warning(request, 'Form Invalid!')
            elif 'programToUnassign' in request.POST:
                if unassign_program_form.is_valid():
                    user = unassign_program_form.cleaned_data['user_unassign']
                    program = unassign_program_form.cleaned_data['programToUnassign']
                    UPJunction.objects.filter(user=user, program=program).delete()
                    messages.success(request, 'Program Unassigned!')
            elif 'videoToUnassign' in request.POST:
                print('hits')
                if unassign_video_form.is_valid():
                    print('hits')
                    program = unassign_video_form.cleaned_data['program_unassign'] 
                    video = unassign_video_form.cleaned_data['videoToUnassign']
                    PVJunction.objects.filter(program=program, video=video).delete()
                    messages.success(request, 'Video Unassigned!')
            elif 'video' in request.POST:
                if assign_video_form.is_valid():
                    program = assign_video_form.cleaned_data['program']
                    video = assign_video_form.cleaned_data['video']
                    PVJunction.objects.create(
                        program=program,
                        video=video,
                    )
                    messages.success(request, 'Video Assigned to Program!')
            elif 'home_text' in request.POST:
                if home_text_form.is_valid():
                    text = home_text_form.cleaned_data['home_text']
                    home_text = HomePageText.objects.first()
                    home_text.home_text = text
                    home_text.save()
                    messages.success(request, 'Home Page Text Updated!')
            elif 'tier_text' in request.POST:
                if tier_text_form.is_valid():
                    tier = tier_text_form.cleaned_data['tier']
                    text = tier_text_form.cleaned_data['tier_text']
                    price = tier_text_form.cleaned_data['tier_price']
                    tier_text = TierText.objects.get(tier=tier)
                    tier_text.tier_text= text
                    tier_text.tier_price = price
                    tier_text.save()
                    messages.success(request, 'Tier Text Updated!')
            elif 'code' in request.POST:
                if trial_code_form.is_valid():
                    code = trial_code_form.cleaned_data['code']
                    trial_code = TrialCode.objects.get(pk=1)
                    if trial_code:
                        trial_code.code = code
                        trial_code.save()
                        messages.success(request, 'Trial Code Updated!')
            elif 'username' in request.POST:
                username = request.POST.get('username')
                
                try:
                    user = User.objects.get(username=username)
                    up_junctions = UPJunction.objects.filter(user=user)
                    table = UPJunctionTable(up_junctions)
                    context = {'user': user, 'table': table}
                    return render(request, 'user_info.html', context)
                except ObjectDoesNotExist:
                    messages.warning(request, 'User not found')
                    return redirect('control_panel')
        context = {
            'video_form': video_form,
            'delete_video_form': delete_video_form,
            'program_form': program_form,
            'delete_program_form': delete_program_form,
            'assign_program_form': assign_program_form,
            'assign_video_form': assign_video_form,
            'unassign_program_form': unassign_program_form,
            'video_table': video_table,
            'unassign_video_form': unassign_video_form,
            'program_table': program_table,
            'user_table': user_table,
            'home_text_form': home_text_form,
            'tier_text_form': tier_text_form,
            'trial_code_form': trial_code_form,
        }
        assign_program_form = AddVideo()
        return render(request, 'control_panel.html', context = context)
    
def program_detail(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    context = {'program': program}
    return render(request, 'program_detail.html', context)

@login_required
def program(request):
    complete_form = CompleteProgramForm(request.POST or None)
    program_name = request.GET.get('name')
    program_date = request.GET.get('date')
    program = Program.objects.get(name=program_name)
    if program_date:
        try:
            program_date = datetime.strptime(program_date, '%b. %d, %Y').date()
        except ValueError:
            program_date = datetime.strptime(program_date, '%B %d, %Y').date()
        junction_obj = UPJunction.objects.filter(start_date=program_date, user= request.user).first()
    else:
        junction_obj = UPJunction.objects.filter(start_date=timezone.now(), user= request.user).first()

    completed = junction_obj.completed
    videos = Video.objects.filter(pvjunction__program=program)
    for video in videos:
        video.video_link = video.video_link.replace("watch?v=", "embed/")
    if not junction_obj.completed:
        if request.method == 'POST':
            if 'complete' in request.POST:
                completed = complete_form['complete']
                if completed:
                    junction_obj.completed = True
                    junction_obj.completion_date = timezone.now()
                    junction_obj.save()
                    messages.success(request, 'Program Completed!')
                    return render(request, 'program.html', {'program': program, 'videos': videos, 'complete_program_form': complete_form, 'completed':True})
        return render(request, 'program.html', {'program': program, 'videos': videos, 'complete_program_form': complete_form})
    return render(request, 'program.html', {'program': program, 'videos': videos, 'completed':True})

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def pagelogout(request):
        logout(request)
        return redirect('index')

@login_required
def subscription(request):
    tier1 = TierText.objects.get(tier=1)
    tier2 = TierText.objects.get(tier=2)
    tier3 = TierText.objects.get(tier=3)
    trial_code_form = TrialCodeForm(request.POST or None)
    f = SubscriptionForm(request.POST or None)
    if request.method == 'POST':
        if 'plans' in request.POST:
            if f.is_valid():
                request.session['subscription_plan'] = request.POST.get('plans')
                return redirect('process_subscription')
            else:
                f = SubscriptionForm()
        elif 'code' in request.POST:
            if trial_code_form.is_valid():
                code = trial_code_form.cleaned_data['code']
                actual_code = TrialCode.objects.get(pk=1)
                if actual_code.code == code:
                    if request.user.groups.filter(name='Tier1').exists():
                        messages.warning(request, 'You are already subscribed to Tier 1!')
                        return render(request, 'subscription.html', locals())
                    else:
                        user = request.user
                        group = Group.objects.get(name='Tier1')
                        user.groups.add(group)
                        user.save()
                        messages.success(request, 'Trial Code Accepted! You are now subscribed to Tier 1!')
                else:
                    messages.warning(request, 'Invalid Trial Code!')
            else:
                trial_code_form = TrialCodeForm()
    
    return render(request, 'subscription.html', locals())

def process_subscription(request):

    subscription_plan = request.session.get('subscription_plan')
    host = request.get_host()
    tier1_price = str(TierText.objects.get(tier=1).tier_price)
    tier2_price = str(TierText.objects.get(tier=2).tier_price)
    tier3_price = str(TierText.objects.get(tier=3).tier_price)
    if subscription_plan == 'Tier 1':
        price = tier1_price
        billing_cycle = 1
        billing_cycle_unit = "M"
    elif subscription_plan == 'Tier 2':
        price = tier2_price
        billing_cycle = 6
        billing_cycle_unit = "M"
    else:
        price = tier3_price
        billing_cycle = 1
        billing_cycle_unit = "M"


    paypal_dict  = {
        "cmd": "_xclick-subscriptions",
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        "a3": price,  # monthly price
        "p3": billing_cycle,  # duration of each unit (depends on unit)
        "t3": billing_cycle_unit,  # duration unit ("M for Month")
        "src": "1",  # make payments recur
        "sra": "1",  # reattempt payment on payment error
        "no_note": "1",  # remove extra notes (optional)
        'item_name': subscription_plan,
        'custom': request.user.id,
        'currency_code': 'USD',
        'notify_url': 'https://root-and-rise-daily-movement.herokuapp.com/' + '/paypal_webhook/',
        'return_url': 'https://root-and-rise-daily-movement.herokuapp.com/' ,
        # 'cancel_return': 'http://{}{}'.format(host,
        #                                       reverse('canceled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
    return render(request, 'process_subscription.html', locals())

@csrf_exempt
def paypal_webhook(request):
    if request.method == 'POST':
        # Parse the query string payload from PayPal
        payload = QueryDict(request.body.decode('utf-8'))
        event_type = payload.get('txn_type')
        
        if event_type == 'subscr_signup' or event_type == 'subscr_payment':
            # Extract the user ID and subscription plan from the webhook data
            user_id = payload.get('custom')
            subscription_plan = payload.get('item_name')

            # Get the user and group
            user = User.objects.get(id=user_id)
            group_name = get_group_name(subscription_plan)
            new_group = Group.objects.get(name=group_name)

            # Check if the user already has a group
            user_groups = user.groups.all()
            if user_groups:
                old_group = user_groups[0]
                # Remove the user from the old group if the new group is different
                if old_group.name != new_group.name:
                    old_group.user_set.remove(user)

            # Add the user to the new group
            new_group.user_set.add(user)
        
        # Return a 200 OK response to PayPal
        response = HttpResponse(status=200)
        response['X-CSRFToken'] = request.COOKIES.get('csrftoken')
        return response
    else:
        # Return a 405 Method Not Allowed response for non-POST requests
        return HttpResponse(status=405)

def get_group_name(item_name):
    # Map the subscription plan names to the corresponding group names
    if item_name == 'Tier 1':
        return 'Tier1'
    elif item_name == 'Tier 2':
        return 'Tier2'
    else:
        return 'Tier3'

class PaypalSuccess(TemplateView):
    template_name = 'paypal_success.html'

class PayPalCancel(TemplateView):
    template_name = 'paypal_cancel.html'

def remove_group(request, user_id):
    # Get the user
    user = User.objects.get(id=user_id)
    
    # Check if the user has a group assigned
    if user.groups.exists():
        # Get the group
        group = user.groups.first()
        
        # Remove the user from the group
        group.user_set.remove(user)
        
    # Redirect to the user's profile page
    messages.success(request, 'Removed subscription from ' + str(user.username))
    return redirect('user_info')


