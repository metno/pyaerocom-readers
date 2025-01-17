import abc
import inspect
from .Data import Data
from .Station import Station
from .Reader import Reader
from .Engine import Engine
from .Filter import VariableNameFilter, Filter, filters, FilterFactory


class UnknownFilterException(Exception):
    pass


class AutoFilterReader(Reader):
    """This helper class applies automatically all filters on the Reader methods
    Reader.data, Reader.stations and Reader.variables. For this to work, the
    reader needs to implement _unfiltered_data, _unfiltered_stations and
    _unfiltered_variables.

    It adds also an overwritable classmethod supported_filters() listing all
    possible filters. This is both used for the AutoFilterEngine, and for the
    check_filters method which should be used during initialization when
    filters are given.

    The implementation must also use _set_filters() to add the filters from __init__.
    """

    @classmethod
    def supported_filters(cls) -> list[Filter]:
        """Get the default list of implemented filters.

        :return: list of filters
        """
        # remember to add all filters here also to the api.rst documentation
        supported = "variables,stations,countries,bounding_boxes,duplicates,time_bounds,time_resolution,flags,time_variable_station,altitude,relaltitude,valleyfloor_relaltitude".split(
            ","
        )
        return [filters.get(name) for name in supported]

    def _set_filters(self, filters):
        supported = set()
        for sf in self.supported_filters():
            supported.add(sf.__class__)

        if isinstance(filters, dict):
            filtlist = []
            for name, kwargs in filters.items():
                filtlist.append(FilterFactory().get(name, **kwargs))
            filters = filtlist
        for filt in filters:
            if filt.__class__ not in supported:
                raise UnknownFilterException(
                    f"Filter {filt.__class__} not supported in {supported}."
                )
        self._filters = filters

    def _get_filters(self) -> list[Filter]:
        """Get a list of filters actually set during initialization of this object.

        :return: list of filters
        """
        return self._filters

    @abc.abstractmethod
    def _unfiltered_data(self, varname) -> Data:
        pass

    @abc.abstractmethod
    def _unfiltered_stations(self) -> dict[str, Station]:
        pass

    @abc.abstractmethod
    def _unfiltered_variables(self) -> list[str]:
        pass

    def variables(self) -> list[str]:
        vars = self._unfiltered_variables()
        for fi in self._get_filters():
            vars = fi.filter_variables(vars)
        return vars

    def stations(self) -> dict[str, Station]:
        stats = self._unfiltered_stations()
        for fi in self._get_filters():
            stats = fi.filter_stations(stats)
        return stats

    def data(self, varname) -> Data:
        for fi in self._get_filters():
            if isinstance(fi, VariableNameFilter):
                varname = fi.reader_varname(varname)
        dat = self._unfiltered_data(varname)
        stats = self._unfiltered_stations()
        vars = self._unfiltered_variables()
        for fi in self._get_filters():
            dat = fi.filter_data(dat, stats, vars)
        return dat


class AutoFilterEngine(Engine):
    """The AutoFilterEngine class implements the supported_filters and
    args method using introspection from the corresponding reader-class.
    The reader_class method needs therefore to be implemented by this class.

    """

    @abc.abstractmethod
    def reader_class(self) -> AutoFilterReader:
        """return the class of the corresponding reader

        :return: the class returned from open
        """
        pass

    def supported_filters(self) -> list[Filter]:
        """The supported filters by this Engine. Maps to the Readers supported_filters.

        :return: a list of filters
        """
        return self.reader_class().supported_filters()

    def args(self):
        sig = inspect.signature(self.reader_class().__init__)
        pars = tuple(sig.parameters.keys())
        return pars[:]

    def open(self, *args, **kwargs) -> Reader:
        return self.reader_class()(*args, **kwargs)
