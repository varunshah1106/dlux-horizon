import logging

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from dlux.exceptions import AuthException


LOG = logging.getLogger(__name__)


class Login(AuthenticationForm):
    """ Form used for logging in a user.

    Handles authentication with Keystone by providing the domain name, username
    and password. A scoped token is fetched after successful authentication.

    A domain name is required if authenticating with Keystone V3 running
    multi-domain configuration.

    If the user authenticated has a default project set, the token will be
    automatically scoped to their default project.

    If the user authenticated has no default project set, the authentication
    backend will try to scope to the projects returned from the user's assigned
    projects. The first successful project scoped will be returned.

    Inherits from the base ``django.contrib.auth.forms.AuthenticationForm``
    class for added security features.
    """
    controller = forms.ChoiceField(label=_("Controller"), required=False)
    username = forms.CharField(label=_("User Name"))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'password', 'controller']
        if getattr(settings,
                   'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT',
                    False):
            #self.fields['domain'] = forms.CharField(label=_("Domain"),
            #                                        required=True)
            self.fields.keyOrder = ['username', 'password', 'controller']
        self.fields['controller'].choices = self.get_controller_choices()
        if len(self.fields['controller'].choices) == 1:
            self.fields['controller'].initial = self.fields['controller'].choices[0][0]
            self.fields['controller'].widget = forms.widgets.HiddenInput()

    @staticmethod
    def get_controller_choices():
        default_ctrl = settings.DEFAULT_CONTROLLER
        return getattr(settings, 'AVAILABLE_CONTROLLERS', [default_ctrl])

    @sensitive_variables()
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        ctrl = self.cleaned_data.get('controller')

        if not (username and password):
            # Don't authenticate, just let the other validators handle it.
            return self.cleaned_data

        try:
            self.user_cache = authenticate(request=self.request,
                                           username=username,
                                           password=password,
                                           controller_url=ctrl)
            msg = 'Login successful for user "%(username)s".' % \
                {'username': username}
            LOG.info(msg)
        except AuthException as exc:
            msg = 'Login failed for user "%(username)s".' % \
                {'username': username}
            LOG.warning(msg)
            self.request.session.flush()
            raise forms.ValidationError(exc)
        self.check_for_test_cookie()
        return self.cleaned_data

