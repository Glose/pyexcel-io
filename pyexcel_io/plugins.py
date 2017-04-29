"""
    pyexcel_io.plugins
    ~~~~~~~~~~~~~~~~~~~

    factory for getting readers and writers

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from lml.loader import scan_plugins
from lml.plugin import PluginManager
from lml.registry import PluginList, PluginInfo

import pyexcel_io.utils as ioutils
import pyexcel_io.manager as manager
import pyexcel_io.exceptions as exceptions
import pyexcel_io.constants as constants


ERROR_MESSAGE_FORMATTER = "one of these plugins for %s data in '%s': %s"
UPGRADE_MESSAGE = "Please upgrade the plugin '%s' according to \
plugin compactibility table."
READER_PLUGIN = 'pyexcel-io reader'
WRITER_PLUGIN = 'pyexcel-io writer'


class IOPluginInfo(PluginInfo):
    def keywords(self):
        for file_type in self.file_types:
            yield file_type


class IORegistry(PluginList):
    def add_a_reader(self, submodule=None, file_types=None, stream_type=None):
        return self._add_a_plugin(
            IOPluginInfo(READER_PLUGIN, self._get_abs_path(submodule),
                         file_types=file_types,
                         stream_type=stream_type))

    def add_a_writer(self, submodule=None, file_types=None, stream_type=None):
        return self._add_a_plugin(
            IOPluginInfo(WRITER_PLUGIN, self._get_abs_path(submodule),
                         file_types=file_types,
                         stream_type=stream_type))


class IOManager(PluginManager):
    def __init__(self, plugin_type, known_list):
        PluginManager.__init__(self, plugin_type)
        self.known_plugins = known_list
        self.action = 'read'
        if self.plugin_name == WRITER_PLUGIN:
            self.action = 'write'

    def load_me_later(self, plugin_info):
        PluginManager.load_me_later(self, plugin_info)
        for file_type in plugin_info.keywords():
            manager.register_stream_type(file_type, plugin_info.stream_type)
            manager.register_a_file_type(
                file_type, plugin_info.stream_type, None)

    def register_a_plugin(self, cls, plugin_info):
        """ for dynamically loaded plugin """
        PluginManager.register_a_plugin(self, cls)
        for file_type in plugin_info.keywords():
            manager.register_stream_type(file_type, plugin_info.stream_type)
            manager.register_a_file_type(
                file_type, cls.stream_type, None)

    def get_a_plugin(self, file_type=None, library=None):
        PluginManager.get_a_plugin(self, file_type=file_type, library=library)
        __file_type = file_type.lower()
        plugin = self.load_me_now(__file_type, library=library)
        handler = plugin()
        handler.set_type(__file_type)
        return handler

    def raise_exception(self, file_type):
        plugins = self.known_plugins.get(file_type, None)
        if plugins:
            message = "Please install "
            if len(plugins) > 1:
                message += ERROR_MESSAGE_FORMATTER % (
                    self.action, file_type, ','.join(plugins))
            else:
                message += plugins[0]
            raise exceptions.SupportingPluginAvailableButNotInstalled(message)
        else:
            raise exceptions.NoSupportingPluginFound(
                "No suitable library found for %s" % file_type)

    def get_all_formats(self):
        all_formats = set(list(self.registry.keys()) +
                          list(self.known_plugins.keys()))
        all_formats = all_formats.difference(set([constants.DB_SQL,
                                                  constants.DB_DJANGO]))
        return all_formats


def _get_me_pypi_package_name(module_name):
    root_module_name = module_name.split('.')[0]
    return root_module_name.replace('_', '-')


readers = IOManager(READER_PLUGIN, ioutils.AVAILABLE_READERS)
writers = IOManager(WRITER_PLUGIN, ioutils.AVAILABLE_WRITERS)


def load_plugins(prefix, path, black_list, white_list):
    scan_plugins(
        prefix,  # constants.DEFAULT_PLUGIN_NAME,
        path, black_list, white_list)
