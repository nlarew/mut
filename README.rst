Automatic Installation
----------------------

Mut provides an automatic installation script requiring only ``bash`` and
``curl``, supporting the following platforms:

.. list-table::

   * - OSX
     - Requires `Brew <http://brew.sh/>`_
   * - Debian/Ubuntu
     -
   * - OpenBSD
     - Requires you to install or configure ``bash``, ``pkg_add``, and
       ``doas``.

.. code-block:: sh

   bash -c "$(curl -fsSL https://raw.githubusercontent.com/mongodb/mut/master/install.sh)"
