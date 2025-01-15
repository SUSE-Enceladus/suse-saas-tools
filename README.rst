SUSE SaaS Tools
---------------

A toolchain for handling Software as a Service subscriptions in
cloud frameworks that connects to the SUSE authentication model
via SCC.

Create a Python Virtual Development Environment
-----------------------------------------------

This is a multi Python namespace project. Each component is placed below
the CSP name followed by the service name. To develop on an
individual service, for example the `resolve_customer` service, run
the following commands to create a development environment.

.. code:: shell-session

   $ cd aws/resolve_customer
   $ poetry install
   $ poetry shell
