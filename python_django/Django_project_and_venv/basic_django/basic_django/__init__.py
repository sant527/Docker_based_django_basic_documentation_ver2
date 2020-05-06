from basic_django.celery import app as celery_app

## __all__ affects how from ... import * works.
## import * is to import all symbols that do not begin with an underscore,
## It is a list of strings defining what symbols in a module will be exported when from <module> import * is used on the module.
__all__ = ['celery_app']
