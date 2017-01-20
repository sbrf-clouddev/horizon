/**
 * Copyright 2017 Sberbank
 * All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */
(function () {
  'use strict';

  angular
    .module('horizon.dashboard.admin.docpages')
    .controller('CreateDocPageController', CreateDocPageController)
    .controller('UpdateDocPageController', UpdateDocPageController);

  CreateDocPageController.$inject = [
    '$window',
    'horizon.dashboard.admin.docpages.create-page.service'
  ];
  UpdateDocPageController.$inject = [
    '$window',
    'horizon.dashboard.admin.docpages.update-page.service'
  ];

  function CreateDocPageController($window, createPageService) {
    var ctrl = this;

    ctrl.createPage = createPage;

    function createPage() {
      createPageService.perform().then(function() {
        $window.location.reload();
      });
    }
  }

  function UpdateDocPageController($window, updatePageService) {
    var ctrl = this;

    ctrl.updatePage = updatePage;

    function updatePage(pageId) {
      updatePageService.perform(pageId).then(function() {
        $window.location.reload();
      });
    }
  }

})();
