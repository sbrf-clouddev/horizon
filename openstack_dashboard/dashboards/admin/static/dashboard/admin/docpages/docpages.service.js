(function() {
  'use strict';

  var formSchema = {
    'type': 'object',
    'properties': {
      'name': {
        'title': gettext('Name'),
        'type': 'string'
      },
      'content': {
        'title': gettext('Content'),
        'type': 'string'
      },
      'url': {
        'title': gettext('Linked to'),
        'type': 'string'
      }
    },
    'required': ['name', 'content']
  };

  angular
    .module('horizon.dashboard.admin.docpages')
    .service('horizon.dashboard.admin.docpages.create-page.service', createPage)
    .service('horizon.dashboard.admin.docpages.update-page.service', updatePage);

  function getFormSpec(apiService, isUpdate) {
    return apiService.get('/api/docpages/urls/')
                     .then(function(data) {
                       var urls = $.map(data.data.items, function(item) {
                             return {
                               value: item,
                               name: item
                             };
                           });
                       urls.unshift({'value': '', 'name': gettext('None')});
                       return [
                         {
                           'key': 'name',
                           'readonly': isUpdate
                         },
                         {
                           'key': 'url',
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

  function createPage(modalFormService, apiService, toastService) {
    return {
      perform: perform
    };

    function onSuccess() {
      toastService.add('success', gettext('Page was successfully created.'));
    }

    function onError() {
      toastService.add('error', gettext('Unable to create the page.'));
    }

    function perform() {
      return getFormSpec(apiService, false)
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

    function onError() {
      toastService.add('error', gettext('Unable to update the page.'));
    }

    function perform(pageId) {
      return $q.all([getFormSpec(apiService, true),
                     apiService.get('/api/docpages/' + pageId + '/')])
               .then(function(results) {
                 var config = {
                       title: gettext('Update Page'),
                       schema: formSchema,
                       form: results[0],
                       model: results[1].data
                     };
                 return modalFormService.open(config);
               })
               .then(function(ctx) {
                 return apiService.patch('/api/docpages/' + ctx.model.id + '/', ctx.model);
               })
               .then(onSuccess, onError);
    }
  }

})();
