import abc
from .Data import Data
from .Station import Station
from .Filter import Filter, filters


class Reader(abc.ABC):
    """Baseclass for timeseries. This can be used with a context manager"""

    @abc.abstractmethod
    def __init__(self, *, filters=None):
        """Initialize the reader.

        This function is usually called from the Engine's open function.
        All parameters should also be listed in the Engine's args function.

        :param filters: list of filters, or dict of (name, kwargs) for FilterFactory
        """
        pass

    def metadata(self) -> dict[str, str]:
        """Metadata set by the datasource.

        The reader-implementation might add metadata depending on the data-source
        to this method.

        :return dictionary with different metadata
        """
        return dict()

    @abc.abstractmethod
    def data(self, varname: str) -> Data:
        """Return all data for a variable

        :param varname: variable name as returned from variables
        :return: a data object
        """
        pass

    @abc.abstractmethod
    def stations(self) -> dict[str, Station]:
        """Dictionary of all stations available for this reader.

        :return: dictionary with station-id as returned from data to Station metadata.
        """
        pass

    @abc.abstractmethod
    def variables(self) -> list[str]:
        """List all variables available in this reader.

        The variable-names returned here should already be change if a
        VariableNameChanger is used.

        :return: List of variables names.
        """
        pass

    @abc.abstractmethod
    def close(self) -> None:
        """Cleanup code for the reader.

        This method will automatically be called when going out of context.
        Implement as dummy (pass) if no cleanup needed.
        """
        pass

    def __enter__(self):
        """Context managaer function

        :return: context-object
        """
        return self

    def __exit__(self, type, value, traceback):
        """Context manager function.

        The default implementation calls the close function.
        """
        self.close()
        return
