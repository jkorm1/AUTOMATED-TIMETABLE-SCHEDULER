from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import StudentProfile, LecturerProfile

class CustomLoginForm(AuthenticationForm):
    index_or_staff_id = forms.CharField(label='Index Number / Staff ID', required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')  
        password = cleaned_data.get('password')
        id_value = cleaned_data.get('index_or_staff_id')

        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid email or password.")

        # Additional check: match ID with profile
        if user.is_student:
            try:
                if user.studentprofile.index_number != id_value:
                    raise forms.ValidationError("Index number mismatch.")
            except StudentProfile.DoesNotExist:
                raise forms.ValidationError("Student profile not found.")
        elif user.is_lecturer:
            try:
                if user.lecturerprofile.staff_id != id_value:
                    raise forms.ValidationError("Staff ID mismatch.")
            except LecturerProfile.DoesNotExist:
                raise forms.ValidationError("Lecturer profile not found.")

        self.user_cache = user
        return cleaned_data

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    index_number = forms.CharField(required=False)
    staff_id = forms.CharField(required=False)
    is_student = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        is_student = cleaned_data.get('is_student')
        index_number = cleaned_data.get('index_number')
        staff_id = cleaned_data.get('staff_id')

        if is_student:
            if not index_number:
                raise forms.ValidationError("Index number is required for students.")
        else:
            if not staff_id:
                raise forms.ValidationError("Staff ID is required for lecturers.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        is_student = self.cleaned_data.get('is_student')
        if commit:
            user.save()
            if is_student:
                StudentProfile.objects.create(user=user, index_number=self.cleaned_data['index_number'])
            else:
                LecturerProfile.objects.create(user=user, staff_id=self.cleaned_data['staff_id'])

        return user

class CustomRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    is_student = forms.BooleanField(required=False, widget=forms.HiddenInput())
    is_lecturer = forms.BooleanField(required=False, widget=forms.HiddenInput())

    # Shared
    secondary_email = forms.EmailField(required=True)
    
    # Student fields
    index_number = forms.CharField(required=False)
    program = forms.CharField(required=False)
    level = forms.CharField(required=False)

    # Lecturer fields
    staff_id = forms.CharField(required=False)
    department = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data