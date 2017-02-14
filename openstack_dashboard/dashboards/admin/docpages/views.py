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

from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon.utils import functions as utils
from horizon import views

from openstack_dashboard.dashboards.admin.docpages import models
from openstack_dashboard.dashboards.admin.docpages \
    import tables as page_tables


class IndexView(tables.DataTableView):
    table_class = page_tables.DocPagesTable
    template_name = 'admin/docpages/index.html'
    page_title = _("Doc Pages")

    def has_prev_data(self, table):
        return getattr(self, "_prev", False)

    def has_more_data(self, table):
        return getattr(self, "_more", False)

    def get_data(self):
        def clamp(x, minv, maxv):
            return max(minv, min(x, maxv))

        request = self.request
        marker = request.GET.get(
            page_tables.DocPagesTable._meta.prev_pagination_param, None
        )
        if marker is None:
            marker = request.GET.get(
                page_tables.DocPagesTable._meta.pagination_param, '1'
            )

        try:
            docpages = models.DocPage.objects.all().order_by('pk')
            paginator = Paginator(
                docpages, per_page=utils.get_page_size(request)
            )
            cur_page = clamp(int(marker), 1, paginator.num_pages)
            self.table.cur_page = cur_page
            self._more = cur_page < paginator.num_pages
            self._prev = cur_page > 1
            return paginator.page(cur_page)
        except Exception:
            self._more = self._prev = False
            exceptions.handle(self.request,
                              _('Unable to retrieve doc pages list.'))
            return []


class ViewView(views.HorizonTemplateView):
    template_name = 'admin/docpages/view.html'
    page_title = ''

    def get_context_data(self, page, **kwargs):
        context = super(ViewView, self).get_context_data(**kwargs)
        try:
            context['page'] = models.DocPage.objects.get(url=page)
        except models.DocPage.DoesNotExist:
            raise exceptions.NotFound
        except Exception:
            exceptions.handle(self.request, _('Unable to view doc page.'))
        return context


class HelpView(views.HorizonTemplateView):
    template_name = 'admin/docpages/syntax.html'
    page_title = ''
