from django import forms
from cdh.core.forms import TemplatedForm, TemplatedModelForm, \
    BootstrapCheckboxInput, BootstrapSelect
from djangosaml2idp.models import ServiceProvider

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


class SPCreateForm(TemplatedForm):

    name = forms.CharField(
        help_text="Not required",
        required=False
    )

    description = forms.CharField(
        widget=forms.Textarea,
        help_text="Not required",
        required=False
    )

    entity_id = forms.CharField(
        required=True,
        help_text="Usually the URL of the SP's metadata"
    )

    metadata_url = forms.URLField(
        required=False,
        help_text="The recommended way to create a new SP is let it auto "
                  "import metadata from this URL"
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
        required=False
    )

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
        fields = '__all__'
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
