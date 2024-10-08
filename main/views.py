import json

import requests
from braces import views as braces
from django import forms
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from djangosaml2idp.models import ServiceProvider
from oauth2_provider.models import Application

from main.attribute_map_presets import SC, SC_ALL, UU
from main.forms import ApplicationForm, SPCreateForm, SPForm, UserForm
from main.models import User, UserMail, UserOU


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['service_providers'] = ServiceProvider.objects.all()
        context['openid_applications'] = Application.objects.all()
        context['users'] = User.objects.all()

        return context


class UserCreateView(braces.LoginRequiredMixin, generic.CreateView):
    model = User
    template_name = 'main/user_form.html'
    form_class = UserForm
    success_url = reverse_lazy('main:home')


class UserEditView(braces.LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = 'main/user_form.html'
    form_class = UserForm
    success_url = reverse_lazy('main:home')

    mail_formset = forms.inlineformset_factory(
        User,
        UserMail,
        fields=('email',),
        can_delete=True,
        extra=4
    )

    ou_formset = forms.inlineformset_factory(
        User,
        UserOU,
        fields=('name',),
        can_delete=True,
        extra=4
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['mail_formset'] = kwargs.get(
            'mail_formset',
            self.mail_formset(instance=self.get_object())
        )
        context['ou_formset'] = kwargs.get(
            'ou_formset',
            self.ou_formset(instance=self.get_object())
        )

        return context


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        mail_formset = self.mail_formset(request.POST, instance=self.object)
        ou_formset = self.ou_formset(request.POST, instance=self.object)

        if form.is_valid() and mail_formset.is_valid() and ou_formset.is_valid():
            return self.form_valid(form, mail_formset, ou_formset)
        elif not form.is_valid():
            return self.form_invalid(form)

        return self.render_to_response(
            self.get_context_data(
                form=form,
                mail_formset=mail_formset
            )
        )

    def form_valid(self, form, mail_formset, ou_formset):
        mail_formset.save()
        ou_formset.save()
        return super().form_valid(form)



class SamlSPEditView(braces.LoginRequiredMixin, generic.UpdateView):
    model = ServiceProvider
    template_name = 'main/sp_form.html'
    form_class = SPForm
    success_url = reverse_lazy('main:home')


class SamlSPCreateView(braces.LoginRequiredMixin, generic.FormView):
    template_name = 'main/sp_form_create.html'
    form_class = SPCreateForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        resp = super().form_valid(form)

        sp = ServiceProvider()
        sp.pretty_name = form.cleaned_data['name']
        sp.description = form.cleaned_data['description']
        sp._sign_response = True
        sp._sign_assertion = True
        sp._processor = settings.SAML_IDP_CONFIG['processor']
        sp.entity_id = form.cleaned_data['entity_id']

        if form.cleaned_data['metadata_url']:
            data = requests.get(form.cleaned_data['metadata_url'])
            sp.local_metadata = str(data.text)
            sp.remote_metadata_url = form.cleaned_data['metadata_url']
        else:
            sp.local_metadata = form.cleaned_data['metadata']

        am = form.cleaned_data['attribute_map']
        if am == "UU":
            sp._attribute_mapping = json.dumps(UU, indent=2)
        elif am == "SC":
            sp._attribute_mapping = json.dumps(SC, indent=2)
        elif am == "SC_all":
            sp._attribute_mapping = json.dumps(SC_ALL, indent=2)

        sp.save()

        return resp


class SamlSPDeleteView(braces.LoginRequiredMixin, generic.DeleteView):
    model = ServiceProvider
    success_url = reverse_lazy('main:home')
    template_name = 'main/sp_form_delete.html'


class SamlMetadataView(braces.LoginRequiredMixin, generic.View):

    def dispatch(self, request, sp, *args, **kwargs):
        serviceProvider = ServiceProvider.objects.get(
            pk=sp
        )

        if serviceProvider.remote_metadata_url:
            return HttpResponseRedirect(
                serviceProvider.remote_metadata_url
            )

        if serviceProvider.local_metadata:
            return HttpResponse(
                content=serviceProvider.local_metadata,
                content_type="application/xml"
            )

        raise Http404


class OpenIDApplicationEditView(braces.LoginRequiredMixin, generic.UpdateView):
    model = Application
    template_name = 'main/oidc_form.html'
    form_class = ApplicationForm
    success_url = reverse_lazy('main:home')


class OpenIDApplicationCreateView(braces.LoginRequiredMixin, generic.FormView):
    template_name = 'main/oidc_form_create.html'
    form_class = ApplicationForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        resp = super().form_valid(form)

        app = Application()
        app.name = form.cleaned_data['name']
        app.redirect_uris = form.cleaned_data['redirect_uris']
        app.skip_authorization = form.cleaned_data['skip_authorization']

        # Hardcoded values
        app.user = self.request.user
        app.client_type = "public"
        app.authorization_grant_type = "authorization-code"
        app.hash_client_secret = False
        app.algorithm = "RS256"

        app.save()

        return resp

class OpenIDApplicationDeleteView(braces.LoginRequiredMixin, generic.DeleteView):
    model = Application
    success_url = reverse_lazy('main:home')
    template_name = 'main/oidc_form_delete.html'
