# -*- coding: utf-8 -*-
#
# This file is part of Flask-CeleryExt
# Copyright (C) 2015 CERN.
#
# Flask-CeleryExt is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for more
# details.

"""Simple integration layer between Celery and Flask.

This extension adds a small integration layer between Celery and Flask based on
http://flask.pocoo.org/docs/0.10/patterns/celery/. In addition to support
execution of tasks in a Flask application context, the extension also supports
execution of task in a test request context (e.g. to ensure that before first
request functions have been executed).

Installation
============

The Flask-CeleryExt package is on PyPI so all you need is:

.. code-block:: console

    $ pip install flask-celeryext

Usage
=====

Extension initialization
------------------------

Initialize the extension like this:

    >>> from flask import Flask
    >>> from flask_celeryext import FlaskCeleryExt
    >>> app = Flask('myapp')
    >>> ext = FlaskCeleryExt(app)

or alternatively using the factory pattern:

    >>> app = Flask('myapp')
    >>> ext = FlaskCeleryExt()
    >>> ext.init_app(app)

The extension will create a Celery application. Configuration is by default
loaded from the Flask application:

    >>> celery = ext.celery

Defining tasks
--------------

You can now define tasks using the Celery application. By default the tasks
will be run inside a Flask application context, and thus have access to e.g.
``current_app``:

    >>> from flask import request
    >>> from flask_celeryext import RequestContextTask
    >>> @celery.task
    ... def apptask():
    ...   return request.method

If you need to run tasks inside a Flask request context, simply change the task
base class:

    >>> from flask import current_app
    >>> @celery.task
    ... def reqtask(base=RequestContextTask):
    ...   return current_app.name

Application factory
-------------------

The Celery application is created by a default application factory, which you
can also use separately:

    >>> from flask_celeryext import create_celery_app
    >>> app = Flask('myapp')
    >>> celery = create_celery_app(app)
    >>> @celery.task
    ... def appctx():
    ...     return "test"

It's also possible to provide a custom Celery application factory to the
extension:

    >>> from celery import Celery
    >>> from flask_celeryext import AppContextTask
    >>> def make_celery(app):
    ...     celery = Celery(app.import_name)
    ...     celery.flask_app = app
    ...     celery.Task = AppContextTask
    ...     return celery
    >>> app = Flask('myapp')
    >>> ext = FlaskCeleryExt(app, create_celery_app=make_celery)


Larger applications
-------------------
In a front-end Flask application you will usually only need a minimal Celery
application configured in order for Celery to know which broker to use etc.
This minimal application however does not need to load all tasks upfront, as
especially for larger applications loading many tasks can cause startup time to
increase significantly.
The background worker on the other hand usually needs to load tasks upfront in
order to know which tasks it can handle.

See http://flask-appfactory.readthedocs.org for a solution on using
Flask-CeleryExt in larger applications.

Testing
-------
Testing your celery tasks is rather easy. First ensure that you Celery is
configured to execute tasks eagerly and stores results in local memory:

    >>> app = Flask("testapp")
    >>> app.config.update(dict(
    ...     CELERY_ALWAYS_EAGER=True,
    ...     CELERY_RESULT_BACKEND="cache",
    ...     CELERY_CACHE_BACKEND="memory",
    ...     CELERY_EAGER_PROPAGATES_EXCEPTIONS=True))
    >>> celery = create_celery_app(app)

You can now create your task:

    >>> @celery.task
    ... def test():
    ...     return current_app.name

And finally execute your task:

    >>> r = test.delay()
    >>> r.result
    'testapp'
"""

from __future__ import absolute_import, print_function, unicode_literals

from .app import AppContextTask, RequestContextTask, create_celery_app
from .ext import FlaskCeleryExt
from .version import __version__

__all__ = (
    '__version__', 'AppContextTask', 'RequestContextTask', 'create_celery_app',
    'FlaskCeleryExt',
)
