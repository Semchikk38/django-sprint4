from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm


class RegistrationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
