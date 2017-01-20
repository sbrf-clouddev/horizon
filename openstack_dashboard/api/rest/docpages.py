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

from horizon.utils import doc_pages
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.dashboards.admin.docpages import models


@urls.register
class Urls(generic.View):
    url_regex = r'docpages/urls/$'

    @rest_utils.ajax()
    def get(self, request):
        from openstack_dashboard import urls as app_urls
        avail_urls = doc_pages.enumerate_table_view_urls(app_urls.urlpatterns)
        return {'items': [':'.join(url_pieces) for url_pieces in avail_urls]}


@urls.register
class DocPages(generic.View):
    url_regex = r'docpages/$'

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Creates a new docpage.

        Creates a docpage using the parameters supplied in the POST
        application/json object. The parameters are:

        :param name: the page name (permalink)
        :param content: the content of the page
        :param url: the url the page should be attached to (optional)

        This returns the new page object on success.
        """
        fields = {
            'name': request.DATA['name'],
            'content': request.DATA['content']
        }
        if 'url' in request.DATA:
            fields['url'] = request.DATA['url']
        page = models.DocPage(**fields)
        page.save()
        return rest_utils.CreatedResponse(
            '/api/docpages/%s' % utils_http.urlquote(page.id),
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
            'content': request.DATA['content']
        }
        if 'url' in request.DATA:
            fields['url'] = request.DATA['url']
        models.DocPage.objects.filter(id=page_id).update(**fields)
