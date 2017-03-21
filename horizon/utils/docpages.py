# Copyright 2017 Sberbank
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import wraps

from django.core.urlresolvers import RegexURLPattern
from django.core.urlresolvers import RegexURLResolver
from openstack_auth import user as auth_user
from openstack_auth import utils
import openstack_auth.views
import six

import horizon
from openstack_dashboard.api import keystone
from openstack_dashboard.dashboards.admin.docpages import models


DOCPAGE_ATTR = 'docpageable'
DOCPAGE_CONTAINER = 'docpages'
DOCPAGE_KEY = 'docpage'
LOGIN_VIEW_NAME = 'login'


class DocViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(DocViewMixin, cls).as_view(**initkwargs)
        setattr(view, DOCPAGE_ATTR, True)
        return view

    def get_context_data(self, **kwargs):
        context = super(DocViewMixin, self).get_context_data(**kwargs)
        context[DOCPAGE_KEY] = get_docpage_for_view(
            getattr(self.request.resolver_match, 'view_name', None)
        )
        return context


# monkey patch login view to support docpage linkage
def _patch_login_view(orig_login):
    @wraps(orig_login)
    def login(*args, **kwargs):
        login_docpage = get_docpage_for_view(LOGIN_VIEW_NAME)
        if login_docpage:
            extra_context = kwargs.setdefault('extra_context', {})
            extra_context[DOCPAGE_KEY] = login_docpage
        return orig_login(*args, **kwargs)
    return login


openstack_auth.views.login = _patch_login_view(openstack_auth.views.login)


def _deduce_urlname_to_viewfunc(reverse_dict):
    """Deduce urlname to viewfunc utility.

    The reverse_dict structure contains 2 types of mappings:

    1) named url mapping to url pattern and
    2) view function mapping to url pattern.

    We need to derive third mapping: named url to a view function.
    """
    name_patterns, func_patterns, name_funcs = {}, {}, {}
    for key, value in six.iteritems(reverse_dict):
        if isinstance(key, str):
            name_patterns[key] = value
        else:
            func_patterns[key] = value

    for name, pat in six.iteritems(name_patterns):
        for func, pat1 in six.iteritems(func_patterns):
            if pat == pat1:
                name_funcs[name] = func

    return name_funcs


class AdminProjectCtx(object):
    admin_project = None

    def __init__(self, request):
        self.request = request
        self.old_user = request.user

        if not AdminProjectCtx.admin_project:
            admin_project, _ = keystone.tenant_list(
                request, filters={'name': 'admin'}
            )
            AdminProjectCtx.admin_project = admin_project[0].id

    def __enter__(self):
        endpoint, _ = utils.fix_auth_url_version_prefix(
            self.request.user.endpoint
        )
        unscoped_token = self.request.user.unscoped_token
        auth = utils.get_token_auth_plugin(
            auth_url=endpoint,
            token=unscoped_token,
            project_id=AdminProjectCtx.admin_project
        )
        auth_ref = auth.get_access(utils.get_session())
        new_user = auth_user.create_user_from_token(
            self.request,
            auth_user.Token(auth_ref, unscoped_token=unscoped_token),
            endpoint
        )
        auth_user.set_session_from_user(self.request, new_user)

    def __exit__(self, _type, value, traceback):
        auth_user.set_session_from_user(self.request, self.old_user)


def enumerate_table_view_urls(root_urls_obj=horizon.urls[0]):
    urls = []

    def is_documented(func, name):
        return getattr(func, DOCPAGE_ATTR, False) or name == LOGIN_VIEW_NAME

    def rec(pattern, namespaces=()):
        if isinstance(pattern, RegexURLPattern):
            if is_documented(pattern.callback, pattern.name):
                urls.append(namespaces + (pattern.name,))
        elif isinstance(pattern, RegexURLResolver):
            if pattern.namespace:
                namespaces += (pattern.namespace,)
            name_funcs = _deduce_urlname_to_viewfunc(pattern.reverse_dict)
            for name, func in six.iteritems(name_funcs):
                if is_documented(func, name):
                    urls.append(namespaces + (name,))

            # NOTE(tsufiev): inside RegexURLResolver there can be both
            # more RegexURLResolver-s (which don't get into reverse_dict
            # because they do not define final patterns) and
            # RegexURLPattern which get into reverse_dict and url_patterns
            # list, so we need to rule them out (because they don't
            # contain callback or mapping to view function and cannot be
            # used for determining view type)
            for p in pattern.url_patterns:
                if isinstance(p, RegexURLResolver):
                    rec(p, namespaces)

    for pat in root_urls_obj:
        rec(pat)
    return urls


def get_docpage_for_view(view):
    if not view:
        return None
    if view != LOGIN_VIEW_NAME:
        view = '/'.join(view.split(':')[1:])
    return models.DocPage.objects.filter(linked_view=view).first()
