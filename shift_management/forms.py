from django import forms
from .models import Pool, Lifeguard, Shift, Application, Incident
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class PoolForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'address', 'phone']
        
class PoolFilterForm(forms.Form):
    name = forms.CharField(required=False, label='Name')
    address = forms.CharField(required=False, label='Address')
    phone = forms.CharField(required=False, label="Phone")
    
class LifeguardForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")

    class Meta:
        model = Lifeguard
        fields = ['first_name', 'last_name', 'email', 'phone']

    def save(self, commit=True):
        lifeguard = super().save(commit=False)
        if not lifeguard.user:  # New user
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            lifeguard.user = user
            # Get the group by name
            group_name = "Lifeguards"  # Replace with the name of your group
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                raise ValueError(f"Group '{group_name}' does not exist. Please create it in the admin panel.")
        if commit:
            lifeguard.save()
        return lifeguard
        
class LifeguardFilterForm(forms.Form):
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")
    email = forms.CharField(required=False, label="Email")
    phone = forms.CharField(required=False, label="Phone")
    
class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["pool", "date", "start_time", "end_time"]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        
class ShiftFilterForm(forms.Form):
    pool = forms.ModelChoiceField(queryset=Pool.objects.all(), required=False, label="Pool", empty_label="Choose a pool")
    date = forms.DateField(required=False, label="Date", widget=forms.DateInput(attrs={'type': 'date'}))
    
class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['type', 'pool', 'description']

class IncidentFilterForm(forms.Form):
    type = forms.ChoiceField(
        choices=[("", "All")] + Incident.INCIDENT_TYPES,
        required=False,
        label="Incident Type"
    )
    pool = forms.ModelChoiceField(
        queryset=Pool.objects.all(),
        required=False,
        label="Pool",
        empty_label="Choose a pool"
    )
    start_date_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "date"}),
        label="Start Date"
    )
    end_date_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "date"}),
        label="End Date"
    )
    
class ApplicationFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All")] + Application.STATUS_CHOICES,
        required=False,
        label="Status"
    )
    lifeguard = forms.ModelChoiceField(
        queryset=Lifeguard.objects.all(),
        required=False,
        label="Lifeguard"
    )
