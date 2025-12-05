# talents/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Profile, Collaboration


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'verification_status_badge', 'created_at', 'has_proof_file', 'admin_actions']
    list_filter = ['verification_status', 'created_at']
    search_fields = ['name', 'skills', 'passions']
    readonly_fields = ['created_at', 'verified_at', 'proof_file_preview']
    list_per_page = 20
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('name', 'avatar_preset', 'created_at')
        }),
        ('Compétences et projets', {
            'fields': ('skills', 'passions', 'languages', 'projects')
        }),
        ('Vérification du talent', {
            'fields': ('proof_file', 'proof_file_preview', 'verification_status', 'admin_comment', 'verified_at'),
            'description': 'Examinez le fichier de preuve et décidez de vérifier ce talent'
        }),
    )
    
    actions = ['approve_selected', 'reject_selected']
    
    def verification_status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        color = status_colors.get(obj.verification_status, 'gray')
        status_text = obj.get_verification_status_display()
        
        if obj.verification_status == 'approved':
            status_text = '✅ ' + status_text
        elif obj.verification_status == 'rejected':
            status_text = '❌ ' + status_text
        else:
            status_text = '⏳ ' + status_text
            
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            status_text
        )
    verification_status_badge.short_description = 'Statut'
    verification_status_badge.admin_order_field = 'verification_status'
    
    def has_proof_file(self, obj):
        if obj.proof_file:
            return format_html(
                '<span style="color: green; font-weight: bold;">📎 Fichier joint</span>'
            )
        return format_html(
            '<span style="color: gray;">❌ Aucun fichier</span>'
        )
    has_proof_file.short_description = 'Fichier'
    
    def proof_file_preview(self, obj):
        if obj.proof_file:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<a href="{}" target="_blank" style="display: inline-block; padding: 10px 15px; background: #4F46E5; color: white; border-radius: 8px; text-decoration: none; font-weight: bold;">'
                '<i class="fas fa-download" style="margin-right: 8px;"></i>'
                'Télécharger le fichier de preuve'
                '</a>'
                '<p style="margin-top: 5px; color: #666; font-size: 13px;">Fichier : {}</p>'
                '</div>',
                obj.proof_file.url,
                obj.proof_file.name
            )
        return format_html(
            '<p style="color: #999; font-style: italic;">Aucun fichier de preuve téléchargé</p>'
        )
    proof_file_preview.short_description = "Fichier de preuve"
    
    def admin_actions(self, obj):
        approve_url = reverse('admin:approve_talent', args=[obj.id])
        reject_url = reverse('admin:reject_talent', args=[obj.id])
        view_url = reverse('admin:talents_profile_change', args=[obj.id])
        
        actions_html = f'''
            <div style="display: flex; gap: 5px;">
                <a href="{approve_url}" style="background: #10B981; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
                    ✅ Valider
                </a>
                <a href="{reject_url}" style="background: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
                    ❌ Rejeter
                </a>
                <a href="{view_url}" style="background: #6366F1; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold;">
                    👁 Voir
                </a>
            </div>
        '''
        return format_html(actions_html)
    
    admin_actions.short_description = 'Actions'
    admin_actions.allow_tags = True
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:profile_id>/approve/',
                 self.admin_site.admin_view(self.approve_talent),
                 name='approve_talent'),
            path('<int:profile_id>/reject/',
                 self.admin_site.admin_view(self.reject_talent),
                 name='reject_talent'),
        ]
        return custom_urls + urls
    
    def approve_talent(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
            profile.verification_status = 'approved'
            profile.verified_at = timezone.now()
            profile.admin_comment = f"Talent approuvé par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            profile.save()
            
            self.message_user(
                request,
                f'Le talent "{profile.name}" a été approuvé avec succès ! ✅',
                messages.SUCCESS
            )
        except Profile.DoesNotExist:
            self.message_user(request, "Talent non trouvé", messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:talents_profile_changelist'))
    
    def reject_talent(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
            profile.verification_status = 'rejected'
            profile.verified_at = timezone.now()
            profile.admin_comment = f"Talent rejeté par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            profile.save()
            
            self.message_user(
                request,
                f'Le talent "{profile.name}" a été rejeté. ❌',
                messages.WARNING
            )
        except Profile.DoesNotExist:
            self.message_user(request, "Talent non trouvé", messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:talents_profile_changelist'))
    
    def approve_selected(self, request, queryset):
        updated = queryset.update(verification_status='approved', verified_at=timezone.now())
        for profile in queryset:
            profile.admin_comment = f"Talent approuvé en masse par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            profile.save()
        
        self.message_user(
            request,
            f'{updated} talent(s) approuvé(s) avec succès ! ✅',
            messages.SUCCESS
        )
    
    def reject_selected(self, request, queryset):
        updated = queryset.update(verification_status='rejected', verified_at=timezone.now())
        for profile in queryset:
            profile.admin_comment = f"Talent rejeté en masse par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            profile.save()
        
        self.message_user(
            request,
            f'{updated} talent(s) rejeté(s). ❌',
            messages.WARNING
        )
    
    approve_selected.short_description = "✅ Approuver les talents sélectionnés"
    reject_selected.short_description = "❌ Rejeter les talents sélectionnés"
    
    def save_model(self, request, obj, form, change):
        if 'verification_status' in form.changed_data:
            if obj.verification_status == 'approved':
                obj.verified_at = timezone.now()
                if not obj.admin_comment:
                    obj.admin_comment = f"Talent approuvé par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            elif obj.verification_status == 'rejected':
                obj.verified_at = timezone.now()
                if not obj.admin_comment:
                    obj.admin_comment = f"Talent rejeté par {request.user.username} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
        
        super().save_model(request, obj, form, change)


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'email', 'created_at']
    search_fields = ['titre', 'desc', 'email']
    list_filter = ['created_at']
    list_per_page = 20