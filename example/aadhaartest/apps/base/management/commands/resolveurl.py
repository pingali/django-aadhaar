import sys
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern, Resolver404, get_resolver

from aadhaartest import urls

__all__ = ('resolve_to_name',)

def _pattern_resolve_to_name(self, path):
    match = self.regex.search(path)
    if match:
        name = ""
        if self.name:
            name = self.name
        elif hasattr(self, '_callback_str'):
            name = self._callback_str
        else:
            name = "%s.%s" % (self.callback.__module__, self.callback.func_name)
        return name

def _resolver_resolve_to_name(self, path):
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            try:
                name = pattern.resolve_to_name(new_path)
            except Resolver404, e:
                tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
            else:
                if name:
                    return name
                tried.append(pattern.regex.pattern)
        raise Resolver404, {'tried': tried, 'path': new_path}


# here goes monkeypatching
RegexURLPattern.resolve_to_name = _pattern_resolve_to_name
RegexURLResolver.resolve_to_name = _resolver_resolve_to_name


def resolve_to_name(path, urlconf=None):
    return get_resolver(urlconf).resolve_to_name(path)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        )

    help = 'Show URLs'

    def handle(self, *args , **options):
        target_url = args[0]
        print resolve_to_name(target_url, urls) 

