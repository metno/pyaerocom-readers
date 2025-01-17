import abc


class Engine(abc.ABC):
    """The engine is the 'singleton' generator object for databases of the engines type."""

    @abc.abstractmethod
    def open(self, *, filters=None):
        """open-function of the timeseries, initializing the reader-object, i.e.
        equivalent to Reader(filename_or_object_or_url, *, filters)

        :return pyaro.timeseries.Reader
        :raises UnknownFilterException
        """
        pass

    @property
    @abc.abstractmethod
    def args(self) -> list[str]:
        """return a tuple of parameters to be passed to open_timeseries
        """
        return []

    @property
    @abc.abstractmethod
    def supported_filters(self) -> list[str]:
        """The class-names of the supported filters by this reader.

        If the reader is called with a filter which is not a instance of this class,
        it is supposed to raise a UnknownFilterException. Using a subclass of a filter is
        not allowed unless explicitly listed here.

        :return: list of classnames
        """
        return ["filterclass1", "filterclass2"]

    @property
    @abc.abstractmethod
    def description(self):
        """Get a descriptive string about this pyaro implementation."""
        pass

    @property
    @abc.abstractmethod
    def url(self):
        """Get a url about more information, docs of the datasource-engine.

        This should be the github-url or similar of the implementation.
        """
        pass
