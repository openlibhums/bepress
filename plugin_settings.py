import os

from django.conf import settings

from utils import models

PLUGIN_NAME = 'Bepress Import'
DESCRIPTION = 'Plugin for importing bepress content to Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '0.1'
SHORT_NAME = 'bepress'
DISPLAY_NAME = 'bepress'
MANAGER_URL = 'bepress_index'

BEPRESS_PATH = os.path.join(settings.BASE_DIR, 'files', 'bepress')

def get_self(install_plugin=False):
    defaults = {
        'display_name': DISPLAY_NAME,
        'version': VERSION,
        'press_wide': True,
        'enabled': True,
    }

    self, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        defaults=defaults
    )

    if install_plugin:
        return self, created

    return self


def install():
    plugin, created = get_self(install_plugin=True)

    if created:
        try:
            os.makedirs(BEPRESS_PATH)
        except FileExistsError:
            pass
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))



def hook_registry():
    # On site load, the load function is run
    # for each installed plugin to generate
    # a list of hooks.
    return {}
