SUSE SaaS Tools
---------------

A toolchain for handling Software as a Service subscriptions in
cloud frameworks that connects to the SUSE authentication model
via SCC. The toolchain is provided as OCI container per CSP.
Please find the latest builds at:

https://build.opensuse.org/project/show/Cloud:Tools:SaaS

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
