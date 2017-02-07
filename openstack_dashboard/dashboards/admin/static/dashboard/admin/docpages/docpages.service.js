(function() {
  'use strict';

  var formSchema = {
    'type': 'object',
    'properties': {
      'url': {
        'title': gettext('URL'),
        'type': 'string'
      },
      'name': {
        'title': gettext('Name'),
        'type': 'string'
      },
      'content': {
        'title': gettext('Content'),
        'type': 'string'
      },
      'linked_view': {
        'title': gettext('Linked to'),
        'type': ['null', 'string'],
        'default': null
      }
    },
    'required': ['url', 'name', 'content']
  };

  angular
    .module('horizon.dashboard.admin.docpages')
    .service('horizon.dashboard.admin.docpages.create-page.service', createPage)
    .service('horizon.dashboard.admin.docpages.update-page.service', updatePage);

  function getFormSpec(apiService, auxUrl) {
    return apiService.get('/api/docpages/urls/')
                     .then(function(data) {
                       var urls = $.map(data.data.items, function(item) {
                             return {
                               value: item,
                               name: item
                             };
                           });
                       if (auxUrl) {
                         urls.unshift({value: auxUrl, name: auxUrl});
                       }
                       urls.unshift({'value': null, 'name': gettext('None')});
                       return [
                         {
                           'key': 'url',
                           'readonly': !!auxUrl
                         },
                         'name',
                         {
                           'key': 'linked_view',
                           'type': 'select',
                           'titleMap': urls
                         },
                         {
                           'key': 'content',
                           'type': 'markdown'
                         }
                       ];
                     });
  }

  createPage.$inject = [
    '$q',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service'
  ];
  updatePage.$inject = [
    '$q',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service'
  ];

  function createPage($q, modalFormService, apiService, toastService) {
    return {
      perform: perform
    };

    function onSuccess() {
      toastService.add('success', gettext('Page was successfully created.'));
    }

    function onError(err) {
      if (err && err !== 'escape key press') {
        toastService.add('error', gettext('Unable to create the page.'));
      }
      return $q.reject(err);
    }

    function perform() {
      return getFormSpec(apiService)
               .then(function(formSpec) {
                 var config = {
                     title: gettext('Create Page'),
                     schema: formSchema,
                     form: formSpec,
                     model: {}
                 };
                 return modalFormService.open(config);
               })
               .then(function(ctx) {
                 return apiService.post('/api/docpages/', ctx.model);
               })
               .then(onSuccess, onError);
    }
  }

  function updatePage($q, modalFormService, apiService, toastService) {
    return {
      perform: perform
    };

    function onSuccess() {
      toastService.add('success', gettext('Page was successfully updated.'));
    }

    function onError(err) {
      if (err && err !== 'escape key press') {
        toastService.add('error', gettext('Unable to update the page.'));
      }
      return $q.reject(err);
    }

    function perform(pageId) {
      return apiService.get('/api/docpages/' + pageId + '/')
                       .then(function(pageData) {
                         var page = pageData.data;
                         return getFormSpec(apiService, page.linked_view).then(function(formSpec) {
                           var config = {
                             title: gettext('Update Page'),
                             schema: formSchema,
                             form: formSpec,
                             model: page
                           };
                           return modalFormService.open(config);
                         });
                       })
                       .then(function(ctx) {
                         return apiService.patch('/api/docpages/' + ctx.model.id + '/', ctx.model);
                       })
                       .then(onSuccess, onError);
    }
  }

})();
