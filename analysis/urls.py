from django.urls import path

from . import views

app_name = "analysis"

urlpatterns = [
    path("", views.AnalysisView.as_view(), name="index"),
    path("tab/", views.analysis_tab, name="tab"),
]
