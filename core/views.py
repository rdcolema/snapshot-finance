from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from positions.services.portfolio import get_portfolio_summary


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = get_portfolio_summary()
        context.update(summary)
        return context
