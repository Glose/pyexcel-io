"""
    pyexcel_io.djangobook
    ~~~~~~~~~~~~~~~~~~~

    The lower level handler for django import and export

    :copyright: (c) 2014-2016 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from .constants import (
    MESSAGE_EMPTY_ARRAY,
    MESSAGE_DB_EXCEPTION,
    MESSAGE_IGNORE_ROW,
    DB_DJANGO
)
from .base import (
    NamedContent,
    NewBookReader,
    NewWriter,
    SheetReader,
    SheetWriter,
    from_query_sets,
    is_empty_array,
    swap_empty_string_for_none,
    ReaderFactory,
    WriterFactory
)

    
class DjangoModelReader(SheetReader):
    """Read from django model
    """
    def __init__(self, model):
        self.model = model

    def to_array(self):
        objects = self.model.objects.all()
        if len(objects) == 0:
            return []
        else:
            column_names = sorted(
                [field.attname
                 for field in self.model._meta.concrete_fields])
            return from_query_sets(column_names, objects)


class DjangoModelWriter(SheetWriter):
    def __init__(self, model, batch_size=None):
        self.batch_size = batch_size
        self.mymodel = None
        self.column_names = None
        self.mapdict = None
        self.initializer = None

        self.mymodel, self.column_names, self.mapdict, self.initializer = model

        if self.initializer is None:
            self.initializer = lambda row: row
        if isinstance(self.mapdict, list):
            self.column_names = self.mapdict
            self.mapdict = None
        elif isinstance(self.mapdict, dict):
            self.column_names = [self.mapdict[name]
                                 for name in self.column_names]
        self.objs = []

    def write_row(self, array):
        if is_empty_array(array):
            print(MESSAGE_EMPTY_ARRAY)
        else:
            new_array = swap_empty_string_for_none(array)
            model_to_be_created = self.initializer(new_array)
            if model_to_be_created:
                self.objs.append(self.mymodel(**dict(
                    zip(self.column_names, model_to_be_created)
                )))
            # else
                # skip the row

    def close(self):
        try:
            self.mymodel.objects.bulk_create(self.objs,
                                             batch_size=self.batch_size)
        except Exception as e:
            print(MESSAGE_DB_EXCEPTION)
            print(e)
            for object in self.objs:
                try:
                    object.save()
                except Exception as e2:
                    print(MESSAGE_IGNORE_ROW)
                    print(e2)
                    print(object)
                    continue




class DjangoModelExportAdapter(object):
    def __init__(self, model):
        self.model = model

    def get_name(self):
        return self.model._meta.model_name


class DjangoModelImportAdapter(DjangoModelExportAdapter):

    class InOutParameter(object):
        def __init__(self):
            self.output = None
            self.input = None

    def __init__(self, model):
        DjangoModelExportAdapter.__init__(self, model)
        self.column_names = self.InOutParameter()
        self.column_name_mapping_dict = self.InOutParameter()
        self.row_initializer = self.InOutParameter()

    def set_row_initializer(self, a_function):
        self.row_initializer.input = a_function
        self._process_parameters()

    def set_column_names(self, column_names):
        self.column_names.input = column_names
        self._process_parameters()

    def set_column_name_mapping_dict(self, mapping_dict):
        self.column_name_mapping_dict.input = mapping_dict
        self._process_parameters()

    def get_row_initializer(self):
        return self.row_initializer.output

    def get_column_names(self):
        return self.column_names.output

    def get_column_name_mapping_dict(self):
        return self.column_name_mapping_dict.output

    def _process_parameters(self):
        if self.row_initializer.input is None:
            self.row_initializer.output = lambda row: row
        else:
            self.row_initializer.output = self.row_initializer.input
        if isinstance(self.column_name_mapping_dict.input, list):
            self.column_names.output = self.column_name_mapping_dict.input
            self.column_name_mapping_dict.output = None
        elif isinstance(self.column_name_mapping_dict.input, dict):
            self.column_names.output = [self.column_name_mapping_dict.input[name]
                                        for name in self.column_names.input]
            self.column_name_mapping_dict.output = None
        if self.column_names.output is None:
            self.column_names.output = self.column_names.input


class DjangoModelImporter(object):
    def __init__(self):
        self.adapters = {}

    def append(self, import_adapter):
        self.adapters[import_adapter.get_name()] = import_adapter

    def get(self, name):
        return self.adapters.get(name, None)


class DjangoModelExporter(object):
    def __init__(self):
        self.adapters = []

    def append(self, import_adapter):
        self.adapters.append(import_adapter)


class DjangoBookReader(NewBookReader):
    def __init__(self):
        NewBookReader.__init__(self, DB_DJANGO)

    def open(self, file_name, **keywords):
        raise NotImplementedError()

    def open_stream(self, file_stream, **keywords):
        raise NotImplementedError()

    def open_content(self, file_content, **keywords):
        self.exporter = file_content
        self.load_from_django_models()

    def load_from_django_models(self):
        django_models = self.exporter.adapters
        self.native_book = [NamedContent(adapter.get_name(), adapter.model)
                            for adapter in django_models]

    def read_sheet(self, native_sheet):
        reader = DjangoModelReader(native_sheet.payload)
        return reader.to_array()


class DjangoModelWriterNew(DjangoModelWriter):
    def __init__(self, adapter, batch_size=None):
        self.batch_size = batch_size
        self.mymodel = adapter.model
        self.column_names = adapter.get_column_names()
        self.mapdict = adapter.get_column_name_mapping_dict()
        self.initializer = adapter.get_row_initializer()
        self.objs = []


class DjangoBookWriter(NewWriter):
    def __init__(self):
        NewWriter.__init__(self, DB_DJANGO)

    def open_content(self, file_content, **keywords):
        self.importer = file_content

    def write(self, incoming_dict):
        for sheet_name in incoming_dict:
            model = self.importer.get(sheet_name)
            if model:
                sheet_writer = DjangoModelWriterNew(model)
                sheet_writer.write_array(incoming_dict[sheet_name])
                sheet_writer.close()

    def close(self):
        pass

ReaderFactory.add_factory(DB_DJANGO, DjangoBookReader)
WriterFactory.add_factory(DB_DJANGO, DjangoBookWriter)
