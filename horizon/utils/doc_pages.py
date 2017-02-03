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

from django.core.urlresolvers import RegexURLPattern
from django.core.urlresolvers import RegexURLResolver

import horizon
from openstack_dashboard.dashboards.admin.docpages import models

DOC_ATTR = 'has_docs'
LOGIN_VIEW_NAME = 'login'


class DocViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(DocViewMixin, cls).as_view(**initkwargs)
        setattr(view, DOC_ATTR, True)
        return view

    def get_context_data(self, **kwargs):
        context = super(DocViewMixin, self).get_context_data(**kwargs)
        context['docpage'] = get_docpage_for_view(
            getattr(self.request.resolver_match, 'view_name', None)
        )
        return context


def _deduce_urlname_to_viewfunc(reverse_dict):
    """Deduce urlname to viewfunc utility.

    The reverse_dict structure contains 2 types of mappings:

    1) named url mapping to url pattern and
    2) view function mapping to url pattern.

    We need to derive third mapping: named url to a view function.
    """
    name_patterns, func_patterns, name_funcs = {}, {}, {}
    for key, value in reverse_dict.items():
        if isinstance(key, str):
            name_patterns[key] = value
        else:
            func_patterns[key] = value

    for name, pat in name_patterns.items():
        for func, pat1 in func_patterns.items():
            if pat == pat1:
                name_funcs[name] = func

    return name_funcs


def enumerate_table_view_urls(root_urls_obj=horizon.urls[0]):
    urls = []

    def is_documented(func, name):
        return getattr(func, DOC_ATTR, False) or name == LOGIN_VIEW_NAME

    def rec(pattern, namespaces=()):
        if isinstance(pattern, RegexURLPattern):
            if is_documented(pattern.callback, pattern.name):
                urls.append(namespaces + (pattern.name,))
        elif isinstance(pattern, RegexURLResolver):
            if pattern.namespace:
                namespaces += (pattern.namespace,)
            name_funcs = _deduce_urlname_to_viewfunc(pattern.reverse_dict)
            for name, func in name_funcs.items():
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
    if view:
        view = '/'.join(view.split(':')[1:])
        return models.DocPage.objects.filter(linked_view=view).first()
    return None
