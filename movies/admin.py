from django.contrib import admin
from .models import Movie, Review, ReviewReport

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class ReviewAdmin(admin.ModelAdmin):
    search_fields = ['comment', 'user__username']
    actions = ['hide_reviews', 'restore_reviews']
    
    @admin.action()
    def hide_reviews(self, request, queryset):
        queryset.update(is_hidden=True)
    
    @admin.action()
    def restore_reviews(self, request, queryset):
        queryset.update(is_hidden=False)

class ReviewReportAdmin(admin.ModelAdmin):
    search_fields = ['reason', 'reported_by__username']
    actions = ['hide_reported_reviews', 'delete_reports_restore']
    
    @admin.action()
    def hide_reported_reviews(self, request, queryset):
        for report in queryset:
            report.review.is_hidden = True
            report.review.save()
    
    @admin.action()
    def delete_reports_restore(self, request, queryset):
        for report in queryset:
            report.review.is_hidden = False
            report.review.save()
        queryset.delete()

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewReport, ReviewReportAdmin)