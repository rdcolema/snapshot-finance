from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from ai.models import WeeklySnapshot
from ai.services.client import is_available
from ai.services.generate import generate_bear_case, generate_thesis
from ai.services.theme_gen import generate_themes
from ai.services.thesis_check import check_thesis
from ai.services.weekly_snapshot import get_or_create_weekly_snapshot
from core.models import Theme
from positions.models import Position


class WeeklySnapshotView(LoginRequiredMixin, TemplateView):
    template_name = "ai/weekly.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ai_available"] = is_available()
        context["snapshot"] = WeeklySnapshot.objects.order_by("-week_of").first()
        return context


@login_required
def generate_weekly(request):
    if request.method == "POST":
        force = request.POST.get("force") == "1"
        get_or_create_weekly_snapshot(force=force)
    return redirect("ai:weekly")


@login_required
def thesis_check_view(request, position_id):
    if request.method == "POST":
        position = get_object_or_404(Position, pk=position_id)
        check_thesis(position)
    return redirect("positions:detail", pk=position_id)


@login_required
def generate_thesis_view(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    if request.method == "POST":
        text = generate_thesis(position)
        if text:
            position.thesis = text
            position.thesis_updated_at = timezone.now()
            position.save()
    return render(request, "positions/_thesis.html", {"position": position})


@login_required
def generate_bear_case_view(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    if request.method == "POST":
        text = generate_bear_case(position)
        if text:
            position.bear_case = text
            position.bear_case_updated_at = timezone.now()
            position.save()
    return render(request, "positions/_bear_case.html", {"position": position})


@login_required
def generate_themes_view(request):
    if request.method != "POST":
        return redirect("ai:weekly")

    positions = list(Position.objects.select_related("sector").all())
    if not positions:
        return redirect("ai:weekly")

    theme_data = generate_themes(positions)
    if not theme_data:
        return redirect("ai:weekly")

    created_count = 0
    assigned_count = 0
    for entry in theme_data:
        name = entry.get("name", "").strip()
        if not name:
            continue
        theme, created = Theme.objects.get_or_create(
            name=name,
            defaults={"description": entry.get("description", "")},
        )
        if created:
            created_count += 1

        symbols = [s.upper() for s in entry.get("symbols", [])]
        matching = Position.objects.filter(symbol__in=symbols)
        for pos in matching:
            pos.themes.add(theme)
            assigned_count += 1

    return redirect("ai:weekly")
