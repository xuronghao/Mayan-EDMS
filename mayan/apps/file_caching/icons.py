from __future__ import absolute_import, unicode_literals

from mayan.apps.appearance.classes import Icon

icon_file_caching = Icon(
    driver_name='fontawesome', symbol='warehouse'
)
icon_cache_purge = Icon(
    driver_name='fontawesome-dual', primary_symbol='warehouse',
    secondary_symbol='check'
)
