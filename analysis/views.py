import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from analysis.services.alerts import get_alerts
from analysis.services.concentration import get_concentration_data
from analysis.services.movers import get_movers_data
from analysis.services.valuation import get_valuation_data

TAB_CHOICES = [
    ("concentration", "Concentration"),
    ("valuation", "Valuation"),
    ("movers", "Movers"),
    ("alerts", "Alerts"),
]

TAB_TEMPLATES = {
    "concentration": "analysis/_tab_concentration.html",
    "valuation": "analysis/_tab_valuation.html",
    "movers": "analysis/_tab_movers.html",
    "alerts": "analysis/_tab_alerts.html",
}


def _get_tab_context(tab):
    """Return context dict for the given tab."""
    ctx = {}
    if tab == "concentration":
        data = get_concentration_data()
        ctx["concentration"] = data
        ctx["concentration_json"] = json.dumps(data, default=str)
    elif tab == "valuation":
        ctx["valuation"] = get_valuation_data()
    elif tab == "movers":
        ctx["movers"] = get_movers_data()
    elif tab == "alerts":
        ctx["alerts"] = get_alerts()
    return ctx


class AnalysisView(LoginRequiredMixin, TemplateView):
    template_name = "analysis/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get("tab", "concentration")
        context["tab"] = tab
        context["tab_choices"] = TAB_CHOICES
        context["tab_template"] = TAB_TEMPLATES.get(tab, TAB_TEMPLATES["concentration"])
        context.update(_get_tab_context(tab))
        return context


@login_required
def analysis_tab(request):
    """HTMX endpoint: returns only the tab partial."""
    tab = request.GET.get("tab", "concentration")
    template = TAB_TEMPLATES.get(tab, TAB_TEMPLATES["concentration"])
    ctx = _get_tab_context(tab)
    return TemplateResponse(request, template, ctx)
