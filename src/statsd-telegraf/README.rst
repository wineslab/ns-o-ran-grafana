===========================================================
A Python statsd client with Telegraf-compatible tag support
===========================================================

_This is a fork of `statsd-tags` which is a fork of `pystatsd` package._

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon. More specifically, this is a fork of jsocol's
pystatsd client, with the addition of support for DogTag-compatible
tags.

:Code:          https://github.com/Granitosaurus/statsd-telegraf
:License:       MIT; see LICENSE file
:Issues:        https://github.com/Granitosaurus/statsd-telegraf/issues
:Documentation: https://statsd-tags.readthedocs.io/

Quickly, to use:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.

Telegraf-compatible tags are supported, as well:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('baz', tags={'type': 'response'}) 
    >>> # baz,type=response:1|c


Installing
==========

The easiest way to install statsd is with pip!

You can install from PyPI::

    $ pip install statsd-telegraf

Or GitHub::

    $ pip install -e git+https://github.com/Granitosaurus/statsd-telegraf#egg=statsd-telegraf

Or from source::

    $ git clone https://github.com/Granitosaurus/statsd-telegraf
    $ cd statsd-telegraf
    $ python setup.py install


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
.. _ReadTheDocs: https://statsd-tags.readthedocs.io/en/latest/index.html
