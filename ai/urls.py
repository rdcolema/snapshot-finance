from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("weekly/", views.WeeklySnapshotView.as_view(), name="weekly"),
    path("weekly/generate/", views.generate_weekly, name="generate_weekly"),
    path("thesis-check/<int:position_id>/", views.thesis_check_view, name="thesis_check"),
    path("generate-thesis/<int:position_id>/", views.generate_thesis_view, name="generate_thesis"),
    path("generate-bear-case/<int:position_id>/", views.generate_bear_case_view, name="generate_bear_case"),
    path("generate-themes/", views.generate_themes_view, name="generate_themes"),
]
