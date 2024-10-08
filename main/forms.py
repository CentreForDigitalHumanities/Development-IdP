from django import forms
from django.conf import settings

from cdh.core.forms import TemplatedForm, TemplatedModelForm, \
    BootstrapCheckboxInput, BootstrapSelect
from djangosaml2idp.models import ServiceProvider
from oauth2_provider.models import Application

from main.models import User


class UserForm(TemplatedModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'uid',
            'password',
            'givenName',
            'sn',
            'cn',
            'displayName',
            'schacHomeOrganization',
            'eduPersonPrincipalName',
            'schacPersonalUniqueCode',
            '_eduPersonEntitlement',
            '_eduPersonAffiliation',
            '_isMemberOf',
            'is_active',
            'is_staff',
            'is_superuser',
        ]
        widgets = {
            'is_staff': BootstrapCheckboxInput,
            'is_superuser': BootstrapCheckboxInput,
            'is_active': BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        if 'password' in self.initial and self.initial['password'].startswith(
                'plain'):
            self.initial['password'] = self.initial['password'].split('$', 2)[1]

    def clean_password(self):
        return f"plain${self.cleaned_data['password']}"


class ApplicationForm(TemplatedModelForm):
    class Meta:
        model = Application
        fields = [
            'name',
            'redirect_uris',
            'skip_authorization',
        ]
        widgets = {
            'redirect_uris': forms.Textarea,
            'post_logout_redirect_uris': forms.Textarea,
            'skip_authorization': BootstrapCheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)

        if 'client_secret' in self.initial and self.initial['client_secret'].startswith(
                'plain'):
            self.initial['client_secret'] = self.initial['client_secret'].split('$', 2)[1]

    def clean_client_secret(self):
        return f"plain${self.cleaned_data['client_secret']}"


class SPCreateForm(TemplatedForm):

    name = forms.CharField(
        help_text="Human friendly name, not required",
        required=False
    )

    description = forms.CharField(
        widget=forms.Textarea,
        help_text="Detailed description, not required",
        required=False
    )

    entity_id = forms.CharField(
        required=True,
        help_text="Almost always the URL of the SP's metadata. (e.g. "
                  "'http://localhost:8000/saml/metadata/')"
    )

    metadata_url = forms.URLField(
        required=False,
        help_text="The IdP will import the metadata by fetching it from this "
                  "url, which is the recommended way to create a new SP"
    )

    metadata = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="If the above option doesn't work, copy+paste the metadata "
                  "manually here."
    )

    attribute_map = forms.CharField(
        widget=BootstrapSelect(
            choices=(
                ('UU', 'UU'),
                ('SC', 'SurfConext (sensible)'),
                ('SC_all', 'SurfConext (full)'),
                (None, 'Empty'),
            )
        ),
        help_text="This will load in a preset attribute map for ease of use. "
                  "Depending on your SP, you might need to create your own. ("
                  "It's recommended to load in the full SC attribute map in "
                  "that case, which contains all available attributes)",
        required=False,
        initial='UU',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.HOSTED:
            self.fields['description'].help_text = ("Please fill in contact "
                                                    "details for your app here")
            self.fields['description'].required = True
            self.fields['name'].help_text = "The name of your app"
            self.fields['name'].required = True

    def clean(self):
        cleaned_data = super().clean()

        if (not cleaned_data['metadata'] and not cleaned_data[
           'metadata_url']) or \
            (cleaned_data['metadata'] and cleaned_data['metadata_url']):
            self.add_error('metadata', 'Exactly one of these two fields need '
                                       'to be filled')
            self.add_error('metadata_url', 'Exactly one of these two fields '
                                           'need to be filled')

        return cleaned_data


YES_NO_UNKNOWN = (
    (True, "Yes"),
    (False, "No"),
    (None, "IDP Default"),
)


class SPForm(TemplatedModelForm):

    class Meta:
        model = ServiceProvider
        fields = [
            'pretty_name',
            'entity_id',
            'description',
            'active',
            'remote_metadata_url',
            'local_metadata',
            'metadata_expiration_dt',
            '_attribute_mapping',
        ]
        widgets = {
            'active': BootstrapCheckboxInput,
            '_sign_response': BootstrapSelect(
                choices=YES_NO_UNKNOWN
            ),
            '_sign_assertion': BootstrapSelect(
                choices=YES_NO_UNKNOWN
            ),
            '_signing_algorithm': BootstrapSelect(
                choices=YES_NO_UNKNOWN
            ),
            '_digest_algorithm': BootstrapSelect,
            '_encrypt_saml_responses': BootstrapSelect(
                choices=YES_NO_UNKNOWN
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['_attribute_mapping'].help_text = """
        A dictionary mapping user attributes from the names used in the IdP to
        the desired name in the SAML response. The key should be the name in the
        IdP, the value the name in the SAML Response
        """
        self.fields['remote_metadata_url'].help_text = ""

        if settings.HOSTED:
            self.fields['description'].help_text = ("Please fill in contact "
                                                    "details for your app here")
            self.fields['description'].required = True
            self.fields['pretty_name'].help_text = "The name of your app"
            self.fields['pretty_name'].required = True
