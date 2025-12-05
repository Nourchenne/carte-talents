# talents/forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Collaboration


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    proof_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.zip,.rar'
        }),
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'zip', 'rar']
        )],
        help_text="Formats acceptés : PDF, DOC, DOCX, JPG, PNG, ZIP, RAR (max 10MB)"
    )
    
    class Meta:
        model = Profile
        fields = ["name", "skills", "passions", "languages", "projects", "avatar", "avatar_preset", "proof_file"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Votre nom et prénom"
            }),
            "skills": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 3,
                "placeholder": "Décrivez vos compétences principales..."
            }),
            "passions": forms.Textarea(attrs={
                "class": "form-textarea", 
                "rows": 2,
                "placeholder": "Quelles sont vos passions ?"
            }),
            "languages": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Ex: Français, Anglais, Espagnol"
            }),
            "projects": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 3,
                "placeholder": "Parlez-nous de vos projets..."
            }),
            "avatar": forms.HiddenInput(),
            "avatar_preset": forms.HiddenInput(),
        }


class CollaborationForm(forms.ModelForm):
    class Meta:
        model = Collaboration
        fields = ["titre", "desc", "email"]
        widgets = {
            "titre": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Titre de votre proposition"
            }),
            "desc": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 4,
                "placeholder": "Décrivez votre projet ou recherche..."
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "votre@email.com"
            }),
        }