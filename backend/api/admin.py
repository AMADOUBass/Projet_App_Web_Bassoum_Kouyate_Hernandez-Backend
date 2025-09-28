from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import (
    User,
    Player,
    Event,
    Participation,
    ReportAdmin,
    SeasonStats
)

# ------------------------
# User
# ------------------------
admin.site.register(User)

# ------------------------
# Player
# ------------------------
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'jersey_number', 'is_available')
    search_fields = ('user__username', 'user__email')
    list_filter = ('position', 'is_available')
    ordering = ('user__username',)
    actions = ['mark_unavailable']

    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} joueur(s) marqué(s) comme absent(s).")
    mark_unavailable.short_description = "Marquer comme absent"

# ------------------------
# Event
# ------------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date_event', 'location', 'is_cancelled')
    search_fields = ('title', 'location')
    list_filter = ('event_type', 'date_event', 'is_cancelled')
    ordering = ('-date_event',)

# ------------------------
# Participation
# ------------------------
@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('player', 'event', 'will_attend', 'notified')
    search_fields = ('player__user__username', 'event__title')
    list_filter = ('will_attend', 'event')
    ordering = ('event__date_event',)
    actions = ['mark_all_notified', 'export_participations_csv']

    def mark_all_notified(self, request, queryset):
        updated = queryset.update(notified=True)
        self.message_user(request, f"{updated} participation(s) marquée(s) comme notifiée(s).")
    mark_all_notified.short_description = "Marquer comme notifiée"

    def export_participations_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="participations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Player', 'Event', 'Will Attend', 'Notified'])

        for p in queryset:
            writer.writerow([
                p.player.user.get_full_name() or p.player.user.email,
                p.event.title,
                'Oui' if p.will_attend else 'Non',
                'Oui' if p.notified else 'Non'
            ])
        return response
    export_participations_csv.short_description = "Exporter les participations en CSV"

# ------------------------
# SeasonStats
# ------------------------
@admin.register(SeasonStats)
class SeasonStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'season_year', 'games_played', 'goals', 'assists', 'yellow_cards', 'red_cards')
    list_filter = ('season_year',)
    search_fields = ('player__user__email', 'player__user__username')
    ordering = ('-season_year', '-goals')
    actions = ['export_stats_csv']

    def export_stats_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="season_stats.csv"'
        writer = csv.writer(response)
        writer.writerow(['Player', 'Season', 'Games Played', 'Goals', 'Assists', 'Yellow Cards', 'Red Cards'])

        for stat in queryset:
            writer.writerow([
                stat.player.user.get_full_name() or stat.player.user.email,
                stat.season_year,
                stat.games_played,
                stat.goals,
                stat.assists,
                stat.yellow_cards,
                stat.red_cards
            ])
        return response
    export_stats_csv.short_description = "Exporter les statistiques en CSV"

# ------------------------
# ReportAdmin
# ------------------------
@admin.register(ReportAdmin)
class ReportAdminAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter_type', 'created_by_admin', 'created_at')
    search_fields = ('title', 'created_by_admin__email')
    list_filter = ('reporter_type', 'created_at')
    ordering = ('-created_at',)
    actions = ['export_reports_csv']

    def export_reports_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reports_admin.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Type', 'Created By', 'Created At'])

        for report in queryset:
            writer.writerow([
                report.title,
                report.reporter_type,
                report.created_by_admin.email if report.created_by_admin else "Inconnu",
                report.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response
    export_reports_csv.short_description = "Exporter les rapports en CSV"