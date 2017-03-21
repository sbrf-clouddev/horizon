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

from django.conf import settings
from django.forms import models as django_models
from django.utils import http as utils_http
from django.views import generic

from horizon.utils import docpages
from horizon.utils.docpages import enumerate_table_view_urls
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.api import swift
from openstack_dashboard.dashboards.admin.docpages import models


attach_limit = getattr(settings, 'DOCPAGE_ATTACH_LIMIT', 50)


@urls.register
class Metadata(generic.View):
    url_regex = r'docpages/meta/$'

    @rest_utils.ajax()
    def get(self, request):
        def to_view(url_piece):
            if url_piece and url_piece[0] == 'horizon':
                url_piece = url_piece[1:]
            return '/'.join(url_piece)

        from openstack_dashboard.urls import urlpatterns
        avail_urls = enumerate_table_view_urls(urlpatterns)
        all_views = (to_view(url_pieces) for url_pieces in avail_urls)
        linked_views = models.DocPage.objects.exclude(linked_view='')
        linked_views = set(linked_views.values_list('linked_view', flat=True))
        container_url = None

        if swift.base.is_service_enabled(request, 'swift'):
            with docpages.AdminProjectCtx(request):
                if not swift.swift_container_exists(
                        request, docpages.DOCPAGE_CONTAINER):
                    swift.swift_create_container(
                        request, docpages.DOCPAGE_CONTAINER,
                        {'is_public': True}
                    )
                container = swift.swift_get_container(
                    request, docpages.DOCPAGE_CONTAINER, with_data=False,
                )
                container_url = container.public_url
        return {
            'views': [v for v in all_views if v not in linked_views],
            'attach_limit': attach_limit,
            'container_url': container_url,
        }


@urls.register
class DocPages(generic.View):
    url_regex = r'docpages/page/$'

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
    url_regex = r'docpages/page/(?P<page_id>[^/]+)/$'

    def post(self, request, page_id):
        if swift.base.is_service_enabled(request, 'swift'):
            uploaded_file = request.FILES and request.FILES['file']
            if not uploaded_file:
                return rest_utils.JSONResponse('No file in request', 400)

            with docpages.AdminProjectCtx(request):
                file_obj = (
                    page_id + swift.FOLDER_DELIMITER + uploaded_file.name)
                if swift.swift_object_exists(
                        request, docpages.DOCPAGE_CONTAINER, file_obj):
                    swift.swift_delete_object(
                        request, docpages.DOCPAGE_CONTAINER, file_obj)
                swift.swift_upload_object(
                    request, docpages.DOCPAGE_CONTAINER, file_obj,
                    uploaded_file,
                )
                return rest_utils.JSONResponse(None, 204)
        else:
            return rest_utils.JSONResponse(
                'Cannot upload file(s). File-storage is not available', 400)

    @rest_utils.ajax()
    def get(self, request, page_id):
        page = django_models.model_to_dict(
            models.DocPage.objects.get(pk=page_id)
        )
        files = []
        if swift.base.is_service_enabled(request, 'swift'):
            with docpages.AdminProjectCtx(request):
                if swift.swift_container_exists(
                        request, docpages.DOCPAGE_CONTAINER):
                    files, _ = swift.swift_get_objects(
                        request,
                        docpages.DOCPAGE_CONTAINER,
                        prefix=page['url'] + swift.FOLDER_DELIMITER,
                    )
        page['attachments'] = [{
            'name': f.name.split('/')[-1],
            'size': f.bytes,
            'modified': getattr(f, 'last_modified', None),
            'type': getattr(f, 'content_type', None)
        } for f in files]
        return page

    @rest_utils.ajax(data_required=True)
    def patch(self, request, page_id):
        page = models.DocPage.objects.get(pk=page_id)
        page.name = request.DATA['name']
        page.content = request.DATA['content']
        page.linked_view = request.DATA.get('linked_view', None)
        page.save()

        if swift.base.is_service_enabled(request, 'swift'):
            with docpages.AdminProjectCtx(request):
                if swift.swift_container_exists(
                        request, docpages.DOCPAGE_CONTAINER):
                    for attachment in request.DATA.get(
                            'removed_attachments', []):
                        try:
                            swift.swift_delete_object(
                                request,
                                docpages.DOCPAGE_CONTAINER,
                                page.url + swift.FOLDER_DELIMITER + attachment,
                            )
                        except Exception:
                            pass
