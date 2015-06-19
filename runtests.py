#!/usr/bin/env python

import argparse
import os
import sys

import django
from django.conf import settings


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',

        'moderator',
    ),
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3"
        }
    },
    SILENCED_SYSTEM_CHECKS=["1_7.W001"],
)


def runtests(args):
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, 'setup'):
        django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    try:
        from django.test.runner import DiscoverRunner

        runner_class = DiscoverRunner
        test_args = [args.tests or 'moderator.tests']
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner

        runner_class = DjangoTestSuiteRunner
        test_args = [args.tests or 'tests']

    failures = runner_class(verbosity=args.verbosity, interactive=True,
                            failfast=args.failfast).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', default=1, type=int)
    parser.add_argument('-f', '--failfast', default=False, type=bool)
    parser.add_argument('tests', nargs='?')

    args = parser.parse_args()

    runtests(args)
