(function() {
  'use strict';

  var API_ROOT = '/api/docpages/';
  var PAGE_ROOT = API_ROOT + 'page/';
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
      },
      'attachments': {
        'title': gettext('Attachments'),
        'type': 'object'
      }
    },
    'required': ['url', 'name', 'content']
  };

  angular
    .module('horizon.dashboard.admin.docpages')
    .service('horizon.dashboard.admin.docpages.utils', utils)
    .service('horizon.dashboard.admin.docpages.create-page.service', createPage)
    .service('horizon.dashboard.admin.docpages.update-page.service', updatePage);

  utils.$inject = [
    '$q',
    '$cookies',
    '$window',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service',
    'FileUploader'
  ];
  createPage.$inject = [
    '$q',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service',
    'horizon.dashboard.admin.docpages.utils'
  ];
  updatePage.$inject = [
    '$q',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service',
    'horizon.dashboard.admin.docpages.utils'
  ];

  function utils($q, $cookies, $window, apiService, toastService, FileUploader) {
    return {
      createUploader: createUploader,
      addTotalSizeFilter: addTotalSizeFilter,
      addPreloadedFile: addPreloadedFile,
      doUpload: doUpload,
      getMeta: getMeta
    };

    function createUploader() {
      var uploader = new FileUploader({
        removeAfterUpload: true,
        headers: {
          'X-CSRFToken': $cookies.csrftoken
        }
      });
      return uploader;
    }

    function addTotalSizeFilter(uploader, limit) {
      uploader.filters.push({
        name: 'total-size',
        fn: function(file) {
          var total = file.size;
          $.each(uploader.queue, function(_, item) {
            total += item.file.size;
          });
          return total / (1024 * 1024) < limit;
        }
      });
    }

    function addPreloadedFile(uploader, options) {
      var file = new FileUploader.FileItem(uploader, options);
      file.progress = 100;
      file.isUploaded = true;
      file.isSuccess = true;
      uploader.queue.push(file);
    }

    function doUpload(uploader, pageURL) {
      var result = $q.defer();
      if (uploader.queue.length === 0) {
        result.resolve();
      } else {
        uploader.onBeforeUploadItem = function(item) {
          var url = $window.WEBROOT + PAGE_ROOT + pageURL + '/';
          item.url = url.replace(/\/+/g, '/');
        };
        uploader.onErrorItem = function(item) {
          var msg = gettext('Error uploading file %(name)s.');
          toastService.add('error', interpolate(msg, item.file, true));
        };
        uploader.onCompleteAll = function() {
          result.resolve();
        };
        uploader.uploadAll();
      }

      return result.promise;
    }

    function getMeta(isUpdate, auxUrl) {
      return apiService
               .get(API_ROOT + 'meta/')
               .then(function(data) {
                 var meta = data.data;
                 var attachLimit = meta.attach_limit;
                 var dropMsg = interpolate(
                   gettext('Drop files here or click to select\nMax sum of file sizes is %s MB'),
                   [attachLimit]
                 );
                 var views = $.map(meta.views, function(item) {
                   return {value: item, name: item};
                 });
                 if (auxUrl) {
                   views.unshift({value: auxUrl, name: auxUrl});
                 }
                 views.unshift({value: null, name: gettext('None')});
                 return {
                   spec: [
                     {
                       'key': 'url',
                       'readonly': isUpdate
                     },
                     'name',
                     {
                       'key': 'linked_view',
                       'type': 'select',
                       'titleMap': views
                     },
                     {
                       'key': 'content',
                       'type': 'markdown',
                       'mdHelpUrl': 'markdown-help/'
                     },
                     {
                       'key': 'attachments',
                       'type': 'files',
                       'dropMsg': dropMsg,
                       'fileURL': function(model, item) {
                         var file = item.file.name;
                         var urlSegments = [
                           meta.container_url,
                           encodeURIComponent(model.url),
                           encodeURIComponent(file)
                         ];
                         return urlSegments.join('/');
                       },
                       'onRemoveItem': function(model, item) {
                         if (item.isUploaded) {
                           if (!model.hasOwnProperty('removed_attachments')) {
                             model.removed_attachments = [];
                           }
                           model.removed_attachments.push(item.file.name);
                         }
                       }
                     }
                   ],
                   attachLimit: attachLimit
                 };
               });
    }
  }

  function createPage($q, modalFormService, apiService, toastService, utils) {
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
      return utils.getMeta(false)
               .then(function(meta) {
                 var uploader = utils.createUploader();
                 utils.addTotalSizeFilter(uploader, meta.attachLimit);
                 return modalFormService.open({
                   title: gettext('Create Page'),
                   schema: formSchema,
                   form: meta.spec,
                   model: {
                     attachments: uploader
                   }
                 });
               })
               .then(function(ctx) {
                 var model = ctx.model;
                 var uploader = model.attachments;

                 delete model.attachments;
                 return apiService
                          .post(PAGE_ROOT, model)
                          .then(function() {
                            return utils.doUpload(uploader, model.url);
                          });
               })
               .then(onSuccess, onError);
    }
  }

  function updatePage($q, modalFormService, apiService, toastService, utils) {
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
      return apiService.get(PAGE_ROOT + pageId + '/')
               .then(function(pageData) {
                 var page = pageData.data;
                 var uploader = utils.createUploader();

                 $.each(page.attachments, function(_, item) {
                   var fileOpts = {
                     lastModifiedDate: new Date(item.modified),
                     size: item.size,
                     type: item.type,
                     name: item.name
                   };
                   utils.addPreloadedFile(uploader, fileOpts);
                 });
                 page.attachments = uploader;
                 return utils
                          .getMeta(true, page.linked_view)
                          .then(function(meta) {
                            utils.addTotalSizeFilter(uploader, meta.attachLimit);
                            return modalFormService.open({
                              title: gettext('Update Page'),
                              schema: formSchema,
                              form: meta.spec,
                              model: page
                            });
                          });
               })
               .then(function(ctx) {
                 var model = ctx.model;
                 var uploader = model.attachments;

                 delete model.attachments;
                 return apiService
                          .patch(PAGE_ROOT + model.id + '/', model)
                          .then(function() {
                            return utils.doUpload(uploader, model.url);
                          });
               })
               .then(onSuccess, onError);
    }
  }

})();
