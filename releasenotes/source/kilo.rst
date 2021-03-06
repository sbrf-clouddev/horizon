=========================
Kilo Series Release Notes
=========================

Key New Features
================

* Support for Federated authentication via Web Single-Sign-On -- When
  configured in keystone, the user will be able to choose the authentication
  mechanism to use from those support by the deployment. This feature must be
  enabled by changes to local_settings.py to be utilized. The related settings
  to enable and configure can be found `here
  <http://docs.openstack.org/developer/horizon/topics/settings.html#websso-enabled>`__.

* Support for Theming -- A simpler mechanism to specify a custom theme for
  Horizon has been included. Allowing for use of CSS values for Bootstrap and
  Horizon variables, as well as the inclusion of custom CSS. More details
  available `here
  <http://docs.openstack.org/developer/horizon/topics/settings.html#custom-theme-path>`__

* Sahara UX Improvements -- Dramatic improvements to the Sahara user experience
  have been made with the addition of guided cluster creation and guided job
  creation pages.

* Launch Instance Wizard (beta) -- A full replacement for the launch instance
  workflow has been implemented in AngularJS to address usability issues in the
  existing launch instance workflow. Due to the late inclusion date and limited
  testing, this feature is marked as beta for Kilo and not enabled by default.
  To use the new workflow, the following change to local_settings.py is
  required: ``LAUNCH_INSTANCE_NG_ENABLED = True``. Additionally, you can disable
  the default launch instance wizard with the following:
  ``LAUNCH_INSTANCE_LEGACY_ENABLED = False``. This new work is a view into
  future development in Horizon.

* Nova

  - Allow service disable/enable on Hypervisor
  - Migrate all instances from host
  - Expose serial console

* Cinder

  - Cinder v2 by default
  - Managed/Unmanaged volume support -- allows admin to manage existing
    volumes not managed by cinder, as well as unmanage volumes
  - Volume transfer support between projects
  - Volume encryption metadata support

* Glance

  - View added to allow administrators to view/add/update Glance Metadata
    definitions

* Heat

  - Stack Template view
  - Orchestration Resources Panel
  - Suspend/Resume actions for Stacks
  - Preview Stack view allows users to preview stacks specified in templates
    before creating them.

* Trove

  - Resizing of Trove instances -- changing instance flavor

* Ceilometer

  - Display IPMI meters values from Ceilometer

* New Reusable AngularJS widgets in Horizon:

  - AngularJS table implementation

    + Table drawers -- expandable table content
    + Improved client/server search

  - Transfer table widget

* Configurable web root for Horizon beyond just '/'

Known Issues
============

* Volumes created from snapshots are empty - https://bugs.launchpad.net/horizon/+bug/1447288
* Django 1.8 is not fully supported yet.

Upgrade Notes
=============

* Django 1.7 is now supported.
