Practices
*******************************************************************************

This guide covers **code organization, patterns, and architectural decisions**.
For guidance on code formatting and visual presentation, see the :doc:`style`.

For detailed language-specific practices, see:

* :doc:`practices-python` - Python-specific development practices
* :doc:`practices-rust` - Rust-specific development practices
* :doc:`practices-toml` - TOML configuration practices

This document provides general principles applicable to all languages.

General Principles
===============================================================================

Documentation Standards
-------------------------------------------------------------------------------

Command Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Use long option names, whenever possible, in command line examples. Readers,
  who are unfamiliar with a command, should not have to look up the meanings of
  single-character option names.

  **❌ Avoid:**

  .. code-block:: shell

      git log -n 5 --oneline
      docker run -d -p 8080:80 -v /data:/app/data nginx

  **✅ Prefer:**

  .. code-block:: shell

      git log --max-count=5 --oneline
      docker run --detach --publish 8080:80 --volume /data:/app/data nginx

* Write for readers who may be unfamiliar with the tools being demonstrated.
  Provide context and explanation for complex command sequences.

Quality Assurance
-------------------------------------------------------------------------------

* Be sure to install the Git hooks, as mentioned in the :doc:`environment`
  section. This will save you turnaround time from pull request validation
  failures.

* Consider maintaining or improving code coverage when practical. Even if code
  coverage is at 100%, consider cases which are not explicitly tested.

Architectural Principles
-------------------------------------------------------------------------------

* **Robustness Principle (Postel's Law)**: "Be conservative in what you send; be liberal in what you accept."
* **Immutability First**: Prefer immutable data structures when internal mutability is not required
* **Dependency Injection**: Functions should provide injectable parameters with sensible defaults
* **Exception Chaining**: Never swallow exceptions; chain or properly handle them

Language-Specific Practices
===============================================================================

* :doc:`practices-python` - Python-specific development practices
* :doc:`practices-rust` - Rust-specific development practices
* :doc:`practices-toml` - TOML configuration practices
