from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Pool, Lifeguard, Shift, Application, Incident

from .forms import PoolForm, PoolFilterForm
from .forms import LifeguardForm, LifeguardFilterForm
from .forms import ShiftForm, ShiftFilterForm
from .forms import IncidentForm, IncidentFilterForm
from .forms import ApplicationFilterForm

from .utils import group_required

def custom_404_view(request, exception=None):
    return redirect('login')

# Login view
def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Checking user groups and redirecting
            if user.groups.filter(name='Coordinators').exists():
                return redirect('pool_list')
            elif user.groups.filter(name='Lifeguards').exists():
                return redirect('shift_list_lifeguard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return render(request, 'registration/logout.html')

# List view for models
def list_view(request, model, form_class, template_name, context_name):
    form = form_class(request.GET or None)
    objects = model.objects.all()

    if form.is_valid():
        for field in form.cleaned_data:
            if form.cleaned_data.get(field):
                objects = objects.filter(**{field: form.cleaned_data[field]})

    context = {
        'form': form,
        context_name: objects,
    }
    return render(request, template_name, context)

# Create view for models
def create_view(request, form_class, template_name, redirect_url):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form})

# Update view for models
def update_view(request, pk, model, form_class, template_name, redirect_url):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)
    return render(request, template_name, {'form': form, 'obj': obj})

# Delete view for models
def delete_view(request, pk, model, template_name, redirect_url):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url)
    return render(request, template_name, {'obj': obj})

# Views for Pools
@login_required
@group_required("Coordinators")
def pool_list(request):
    return list_view(request, Pool, PoolFilterForm, 'pool/pool_list.html', 'pools')

@login_required
@group_required("Coordinators")
def pool_create(request):
    return create_view(request, PoolForm, 'pool/pool_form.html', 'pool_list')

@login_required
@group_required("Coordinators")
def pool_update(request, pk):
    return update_view(request, pk, Pool, PoolForm, 'pool/pool_form.html', 'pool_list')

@login_required
@group_required("Coordinators")
def pool_delete(request, pk):
    return delete_view(request, pk, Pool, 'pool/pool_confirm_delete.html', 'pool_list')

# Views for Lifeguards
@login_required
@group_required("Coordinators")
def lifeguard_list(request):
    return list_view(request, Lifeguard, LifeguardFilterForm, 'lifeguard/lifeguard_list.html', 'lifeguards')

@login_required
@group_required("Coordinators")
def lifeguard_create(request):
    if request.method == 'POST':
        form = LifeguardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lifeguard_list')
    else:
        form = LifeguardForm()
    return render(request, 'lifeguard/lifeguard_form.html', {'form': form})

@login_required
@group_required("Coordinators")
def lifeguard_update(request, pk):
    lifeguard = get_object_or_404(Lifeguard, pk=pk)
    if request.method == 'POST':
        form = LifeguardForm(request.POST, instance=lifeguard)
        if form.is_valid():
            form.save()
            return redirect('lifeguard_list')
    else:
        form = LifeguardForm(instance=lifeguard)
    return render(request, 'lifeguard/lifeguard_form.html', {'form': form})

@login_required
@group_required("Coordinators")
def lifeguard_delete(request, pk):
    lifeguard = get_object_or_404(Lifeguard, pk=pk)
    if request.method == 'POST':
        if lifeguard.user:
            lifeguard.user.delete()
        lifeguard.delete()
        messages.success(request, f"Lifeguard {lifeguard.first_name} {lifeguard.last_name} has been deleted.")
        return redirect('lifeguard_list')
    return render(request, 'lifeguard/lifeguard_confirm_delete.html', {'lifeguard': lifeguard})

# Views for Shifts
@login_required
@group_required("Coordinators")
def shift_list(request):
    return list_view(request, Shift, ShiftFilterForm, 'shift/shift_list.html', 'shifts')

@login_required
@group_required("Coordinators")
def shift_create(request):
    return create_view(request, ShiftForm, 'shift/shift_form.html', 'shift_list')

@login_required
@group_required("Coordinators")
def shift_update(request, pk):
    return update_view(request, pk, Shift, ShiftForm, 'shift/shift_form.html', 'shift_list')

@login_required
@group_required("Coordinators")
def shift_delete(request, pk):
    return delete_view(request, pk, Shift, 'shift/shift_confirm_delete.html', 'shift_list')

@login_required
@group_required("Lifeguards")
def shift_list_lifeguard(request):
    form = ShiftFilterForm(request.GET)
    shifts = Shift.objects.filter(
        Q(application__isnull=True) |
        (Q(application__status='R') & ~Q(application__lifeguard__user=request.user))
    )

    if form.is_valid():
        pool = form.cleaned_data.get('pool')
        date = form.cleaned_data.get('date')

        if pool:
            shifts = shifts.filter(pool=pool)

        if date:
            shifts = shifts.filter(date=date)

    return render(request, 'shift/shift_list_lifeguard.html', {'shifts': shifts, 'form': form})

# Views for Applications
@login_required
@group_required("Coordinators")
def application_list(request):
    form = ApplicationFilterForm(request.GET or None)
    applications = Application.objects.all()

    if form.is_valid():
        if form.cleaned_data['status']:
            applications = applications.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['lifeguard']:
            applications = applications.filter(lifeguard=form.cleaned_data['lifeguard'])

    return render(request, 'application/application_list.html', {'applications': applications, 'form': form})

@login_required
@group_required("Coordinators")
def application_status_update(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [choice[0] for choice in Application.STATUS_CHOICES]:
            application.status = status
            application.save()
            return redirect('application_list')
    return render(request, 'application/application_status_update.html', {'application': application})

@login_required
@group_required("Lifeguards")
def application_create(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    lifeguard = get_object_or_404(Lifeguard, user=request.user)

    if Application.objects.filter(shift=shift).exists():
        return redirect('shift_list_lifeguard')

    Application.objects.create(
        shift=shift,
        lifeguard=lifeguard,
        status='O'  # "Pending" status
    )
    return redirect('shift_list_lifeguard')

@login_required
@group_required("Lifeguards")
def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk, lifeguard__user=request.user)
    application.delete()
    return redirect('application_list_lifeguard')

@login_required
@group_required("Lifeguards")
def application_list_lifeguard(request):
    applications = Application.objects.filter(lifeguard__user=request.user)

    # Obsługa formularza filtrowania
    form = ApplicationFilterForm(request.GET)  # Pobieranie danych GET
    if form.is_valid():
        status = form.cleaned_data.get("status")
        lifeguard = form.cleaned_data.get("lifeguard")

        # Filtrowanie na podstawie statusu
        if status:
            applications = applications.filter(status=status)

        # Filtrowanie na podstawie ratownika (jeśli potrzebne)
        if lifeguard:
            applications = applications.filter(lifeguard=lifeguard)

    return render(request, 'application/application_list_lifeguard.html', {
        'applications': applications,
        'form': form,
    })

# Views for Incidents
@login_required
@group_required("Coordinators")
def incident_list(request):
    form = IncidentFilterForm(request.GET or None)
    incidents = Incident.objects.all()

    if form.is_valid():
        if form.cleaned_data['type']:
            incidents = incidents.filter(type=form.cleaned_data['type'])
        if form.cleaned_data['pool']:
            incidents = incidents.filter(pool=form.cleaned_data['pool'])
        if form.cleaned_data['start_date_time']:
            incidents = incidents.filter(date_time__gte=form.cleaned_data['start_date_time'])
        if form.cleaned_data['end_date_time']:
            incidents = incidents.filter(date_time__lte=form.cleaned_data['end_date_time'])

    return render(request, 'incident/incident_list.html', {'incidents': incidents, 'form': form})

@login_required
@group_required("Lifeguards")
def incident_list_lifeguard(request):
    form = IncidentFilterForm(request.GET or None)
    lifeguard = get_object_or_404(Lifeguard, user=request.user)

    incidents = Incident.objects.filter(lifeguard=lifeguard)
    if form.is_valid():
        incident_type = form.cleaned_data.get('type')
        pool = form.cleaned_data.get('pool')
        date_time_from = form.cleaned_data.get('date_time_from')
        date_time_to = form.cleaned_data.get('date_time_to')

        if incident_type:
            incidents = incidents.filter(type=incident_type)
        if pool:
            incidents = incidents.filter(pool=pool)
        if date_time_from:
            incidents = incidents.filter(date_time__gte=date_time_from)
        if date_time_to:
            incidents = incidents.filter(date_time__lte=date_time_to)

    return render(request, 'incident/incident_list_lifeguard.html', {'incidents': incidents, 'form': form})

@login_required
@group_required("Lifeguards")
def incident_create(request):
    lifeguard = get_object_or_404(Lifeguard, user=request.user)

    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.lifeguard = lifeguard
            incident.save()
            return redirect('incident_list_lifeguard')
    else:
        form = IncidentForm()

    return render(request, 'incident/incident_form.html', {'form': form})

@login_required
@group_required("Lifeguards")
def incident_update(request, incident_id):
    incident = get_object_or_404(Incident, pk=incident_id, lifeguard__user=request.user)

    if request.method == "POST":
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('incident_list_lifeguard')
    else:
        form = IncidentForm(instance=incident)

    return render(request, 'incident/incident_form.html', {'form': form})

@login_required
@group_required("Lifeguards")
def incident_delete(request, incident_id):
    incident = get_object_or_404(Incident, pk=incident_id, lifeguard__user=request.user)
    if request.method == "POST":
        incident.delete()
        return redirect('incident_list_lifeguard')
    return render(request, 'incident/incident_confirm_delete.html', {'incident': incident})

# 404 error handling
def custom_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)
