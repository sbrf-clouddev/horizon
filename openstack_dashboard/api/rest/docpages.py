# Copyright 2017 Sberbank
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.forms import models as django_models
from django.utils import http as utils_http
from django.views import generic

from horizon.utils.docpages import enumerate_table_view_urls
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.dashboards.admin.docpages import models


@urls.register
class Urls(generic.View):
    url_regex = r'docpages/urls/$'

    @rest_utils.ajax()
    def get(self, request):
        def to_view(url_piece):
            if url_piece and url_piece[0] == 'horizon':
                url_piece = url_piece[1:]
            return '/'.join(url_piece)

        from openstack_dashboard import urls as app_urls
        avail_urls = enumerate_table_view_urls(app_urls.urlpatterns)
        all_views = (to_view(url_pieces) for url_pieces in avail_urls)
        linked_views = models.DocPage.objects.exclude(linked_view='')
        linked_views = set(linked_views.values_list('linked_view', flat=True))
        return {'items': [v for v in all_views if v not in linked_views]}


@urls.register
class DocPages(generic.View):
    url_regex = r'docpages/$'

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Creates a new docpage.

        Creates a docpage using the parameters supplied in the POST
        application/json object. The parameters are:

        :param url: the page permalink
        :param name: the page name
        :param content: the content of the page
        :param linked_view: the view this page is attached to (optional)

        This returns the new page object on success.
        """
        fields = {
            'url': request.DATA['url'],
            'name': request.DATA['name'],
            'content': request.DATA['content'],
            'linked_view': request.DATA.get('linked_view', None)
        }
        page = models.DocPage.objects.create(**fields)
        return rest_utils.CreatedResponse(
            '/api/docpages/%s/' % utils_http.urlquote(page.id),
            django_models.model_to_dict(page)
        )


@urls.register
class DocPage(generic.View):
    url_regex = r'docpages/(?P<page_id>[^/]+)/$'

    @rest_utils.ajax()
    def get(self, request, page_id):
        return django_models.model_to_dict(
            models.DocPage.objects.get(pk=page_id)
        )

    @rest_utils.ajax(data_required=True)
    def patch(self, request, page_id):
        fields = {
            'name': request.DATA['name'],
            'content': request.DATA['content'],
            'linked_view': request.DATA.get('linked_view', None)
        }
        models.DocPage.objects.filter(pk=page_id).update(**fields)
