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
   .directive('dockpageMarkdown', DocPageMarkdownDirective);

  DocPageMarkdownDirective.$inject = [
    '$showdown',
    '$sanitize'
  ];

  function DocPageMarkdownDirective($showdown, $sanitize) {
    return {
      restrict: 'AE',
      link: function(scope, elem, attrs) {
        if (attrs.dockpageMarkdown) {
          scope.$watch(attrs.dockpageMarkdown, function(newVal) {
            render(newVal);
          });
        } else {
            render(elem.text());
        }

        function render(raw) {
          var html = $showdown.makeHtml(raw);
          if ($showdown.getOption('sanitize')) {
            html = $sanitize(html);
          }
          elem.html(html);
        }
      }
    };
  }

})();
