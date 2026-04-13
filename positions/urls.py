from django.urls import path

from . import views

app_name = "positions"

urlpatterns = [
    path("", views.PositionsView.as_view(), name="index"),
    path("<int:pk>/", views.PositionDetailView.as_view(), name="detail"),
    path("<int:pk>/update-thesis/", views.update_thesis, name="update_thesis"),
    path("<int:pk>/update-bear-case/", views.update_bear_case, name="update_bear_case"),
    path("<int:pk>/update-themes/", views.update_themes, name="update_themes"),
    path("filter/", views.positions_filter, name="filter"),
]
