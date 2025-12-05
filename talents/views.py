# talents/views.py
from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from .models import Profile, Collaboration
from .forms import ProfileForm, CollaborationForm


def talent_list(request):
    query = request.GET.get("q", "")
    # Afficher TOUS les profils
    profiles = Profile.objects.all().order_by("-created_at")

    if query:
        profiles = profiles.filter(
            Q(name__icontains=query)
            | Q(skills__icontains=query)
            | Q(passions__icontains=query)
            | Q(languages__icontains=query)
            | Q(projects__icontains=query)
        )

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES)
        
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            
            # Gérer l'avatar prédéfini
            selected_preset = request.POST.get("avatar_preset")
            if selected_preset:
                try:
                    profile.avatar_preset = int(selected_preset)
                except (ValueError, TypeError):
                    profile.avatar_preset = 1
            else:
                profile.avatar_preset = 1
            
            # Le profil est créé avec le statut "en attente" de vérification
            profile.verification_status = 'pending'
            
            profile.save()
            return redirect(f"{request.path}?success=1")
    else:
        profile_form = ProfileForm()

    return render(
        request,
        "talents/talent_list.html",
        {
            "profiles": profiles,
            "query": query,
            "profile_form": profile_form,
        },
    )


def collaborateur_list(request):
    query = request.GET.get("q", "")
    collaborations = Collaboration.objects.all().order_by("-created_at")

    if query:
        collaborations = collaborations.filter(
            Q(titre__icontains=query)
            | Q(desc__icontains=query)
            | Q(email__icontains=query)
        )

    if request.method == "POST":
        form = CollaborationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?success=1")
    else:
        form = CollaborationForm()

    return render(
        request,
        "talents/collaborateur_list.html",
        {
            "collaborations": collaborations,
            "form": form,
            "query": query,
        },
    )