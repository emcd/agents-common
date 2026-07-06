Maintenance
*******************************************************************************

.. todo:: Github workflows for updating dependecies locks.


Copier
===============================================================================

The project was created from a `Copier template
<https://github.com/emcd/python-project-common/tree/master/template>`_. In
addition to seeding the initial project structure and code, updates from the
template can be incorporated into the project, ensuring adherence to evolving
practices and technologies.

Updates
-------------------------------------------------------------------------------

1. Ensure the working directory is clean (commit or stash changes).

2. Run the update command:
   ::

        copier update --answers-file .auxiliary/configuration/copier-answers.yaml

.. note:: The update process preserves your answers from the previous template
          generation. You can override specific answers using the ``--data``
          option with the update command.
