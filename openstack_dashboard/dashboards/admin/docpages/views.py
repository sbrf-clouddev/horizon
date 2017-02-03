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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import views

from openstack_dashboard.dashboards.admin.docpages import models
from openstack_dashboard.dashboards.admin.docpages \
    import tables as page_tables


class IndexView(tables.DataTableView):
    table_class = page_tables.DocPagesTable
    template_name = 'admin/docpages/index.html'
    page_title = _("Doc Pages")

    def get_data(self):
        try:
            return models.DocPage.objects.all()
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve doc pages list.'))
            return []


class ViewView(views.HorizonTemplateView):
    template_name = 'admin/docpages/view.html'
    page_title = ''

    def get_context_data(self, page_url, **kwargs):
        context = super(ViewView, self).get_context_data(**kwargs)
        try:
            context['page'] = models.DocPage.objects.get(url=page_url)
        except models.DocPage.DoesNotExist:
            raise exceptions.NotFound
        except Exception:
            exceptions.handle(self.request, _('Unable to view doc page.'))
        return context
