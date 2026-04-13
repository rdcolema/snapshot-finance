import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import TemplateView

from ai.models import ThesisCheck
from ai.services.client import is_available as ai_available
from core.models import Sector, Theme
from positions.models import Account, Position
from positions.services.fundamentals import get_fundamentals
from positions.services.portfolio import get_enriched_positions
from positions.services.quotes import get_quote


class PositionsView(LoginRequiredMixin, TemplateView):
    template_name = "positions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        positions = get_enriched_positions()
        context["positions_json"] = json.dumps(positions, default=str)
        context["accounts"] = Account.objects.all()
        context["sectors"] = Sector.objects.all()
        return context


class PositionDetailView(LoginRequiredMixin, TemplateView):
    template_name = "positions/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        position = get_object_or_404(
            Position.objects.select_related("account", "sector").prefetch_related("themes", "lots"),
            pk=kwargs["pk"],
        )
        quote = get_quote(position.symbol) or {}
        fundamentals = get_fundamentals(position.symbol) or {}

        context["position"] = position
        context["quote"] = quote
        context["fundamentals"] = fundamentals
        context["lots"] = position.lots.all()
        context["ai_available"] = ai_available()
        context["all_themes"] = Theme.objects.all()
        context["thesis_checks"] = ThesisCheck.objects.filter(position=position).order_by("-created_at")[:10]
        return context


@login_required
def update_thesis(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    position = get_object_or_404(Position, pk=pk)
    position.thesis = request.POST.get("thesis", "")
    if position.thesis:
        position.thesis_updated_at = timezone.now()
    position.save()
    return render(request, "positions/_thesis.html", {"position": position})


@login_required
def update_bear_case(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    position = get_object_or_404(Position, pk=pk)
    position.bear_case = request.POST.get("bear_case", "")
    if position.bear_case:
        position.bear_case_updated_at = timezone.now()
    position.save()
    return render(request, "positions/_bear_case.html", {"position": position})


@login_required
def update_themes(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    position = get_object_or_404(Position, pk=pk)
    theme_ids = request.POST.getlist("themes")
    position.themes.set(theme_ids)
    all_themes = Theme.objects.all()
    return render(request, "positions/_themes.html", {"position": position, "all_themes": all_themes})


@login_required
def positions_filter(request):
    account_ids = request.GET.getlist("account")
    sector_ids = request.GET.getlist("sector")
    positions = get_enriched_positions(
        account_ids=account_ids or None,
        sector_ids=sector_ids or None,
    )
    return JsonResponse(positions, safe=False, json_dumps_params={"default": str})
