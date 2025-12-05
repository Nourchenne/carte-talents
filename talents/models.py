# talents/models.py
from django.db import models
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    name = models.CharField("Nom", max_length=150, default="Anonyme")
    skills = models.TextField("Compétences", blank=True)
    passions = models.TextField("Passions", blank=True)
    languages = models.CharField("Langues", max_length=200, blank=True)
    projects = models.TextField("Projets réalisés", blank=True)
    
    # avatar uploadé
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # avatar prédéfini
    avatar_preset = models.PositiveSmallIntegerField(
        default=1,
        help_text="Numéro d'avatar prédéfini (1-11)"
    )
    
    # Fichier de preuve pour la vérification
    proof_file = models.FileField(
        "Fichier de preuve",
        upload_to='proofs/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'zip', 'rar']
        )],
        help_text="Téléchargez un fichier prouvant vos talents (PDF, images, documents, archives)"
    )
    
    # Statut de vérification
    verification_status = models.CharField(
        "Statut de vérification",
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    
    # Commentaire de l'admin (pour les rejets)
    admin_comment = models.TextField("Commentaire de l'admin", blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    # Méthode pour obtenir l'URL de l'avatar
    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        
        preset_number = self.avatar_preset or 1
        preset_number = max(1, min(preset_number, 11))
        return f'/static/talents/avatars/{preset_number}.png'
    
    # Propriété pour vérifier si le profil est vérifié
    @property
    def is_verified(self):
        return self.verification_status == 'approved'
    
    # Méthode pour obtenir l'extension du fichier
    def get_file_extension(self):
        if self.proof_file:
            filename = self.proof_file.name
            return filename.split('.')[-1].lower() if '.' in filename else ''
        return ''
    
    # Méthode pour obtenir l'icône du fichier
    def get_file_icon(self):
        ext = self.get_file_extension()
        if ext in ['pdf']:
            return 'fa-file-pdf'
        elif ext in ['doc', 'docx']:
            return 'fa-file-word'
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'fa-file-image'
        elif ext in ['zip', 'rar']:
            return 'fa-file-archive'
        else:
            return 'fa-file'


class Collaboration(models.Model):
    titre = models.CharField("Titre", max_length=200)
    desc = models.TextField("Description")
    email = models.EmailField("Email")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre