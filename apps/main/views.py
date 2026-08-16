from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.barbers.models import BarberProfile
from apps.services.models import Service

from .forms import ContactForm


class HomeView(TemplateView):
    """Bosh sahifa — top xizmatlar va ustalar ko'rsatiladi."""
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)[:6]
        context['barbers'] = BarberProfile.objects.select_related('user').order_by('-rating')[:4]
        return context


class AboutView(TemplateView):
    template_name = 'main/about.html'


class RobotsTxtView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'


class SitemapXmlView(TemplateView):
    template_name = 'sitemap.xml'
    content_type = 'application/xml'


class ContactView(TemplateView):
    template_name = 'main/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Xabaringiz yuborildi! Tez orada bog'lanamiz.")
            return redirect('main:contact')
        return self.render_to_response(self.get_context_data(form=form))
