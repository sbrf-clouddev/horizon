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

from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
import six

from horizon import tables
from openstack_dashboard.dashboards.admin.docpages import models


class DeletePage(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Page",
            u"Delete Pages",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Page",
            u"Deleted Pages",
            count
        )

    def delete(self, request, obj_id):
        models.DocPage.objects.filter(pk=obj_id).delete()


class CreatePage(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Page")
    icon = "plus"
    attrs = {"ng-controller": "CreateDocPageController as modal",
             "ng-click": "modal.createPage()"}

    def get_link_url(self, datum=None):
        return "javascript:void(0);"


class UpdatePage(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Page")
    icon = "pencil"
    attrs = {"ng-controller": "UpdateDocPageController as modal"}

    def get_link_url(self, datum=None):
        obj_id = self.table.get_object_id(datum)
        self.attrs["ng-click"] = "modal.updatePage('%s')" % obj_id
        return "javascript:void(0);"


class ViewPage(tables.LinkAction):
    name = "view"
    verbose_name = _("View Page")
    icon = "eye"
    attrs = {"target": "_blank"}

    def get_link_url(self, datum=None):
        return urlquote(datum.url) + "/"


class DocPagesTable(tables.DataTable):
    url = tables.Column('url', verbose_name=_('Page URL'))
    name = tables.Column('name', verbose_name=_('Page Name'))
    linked_view = tables.Column('linked_view', verbose_name=_('Linked to'))

    def get_marker(self):
        return six.text_type(self._meta.cur_page + 1)

    def get_prev_marker(self):
        return six.text_type(self._meta.cur_page - 1)

    class Meta(object):
        name = "docpages"
        verbose_name = _("Doc Pages")
        table_actions = (tables.NameFilterAction, CreatePage, DeletePage)
        row_actions = (ViewPage, UpdatePage, DeletePage)
        cur_page = 1
