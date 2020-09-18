"""
The module contains PathFinder class which goes through dictionary of errors and gets all paths to elements.

"""
from functools import reduce
from operator import getitem

from typing import Any, Hashable, Union


class PathFinder:
    """
    PathFinder walks through error's dictionary and gets sequences of keys to all elements.

    """

    def __init__(self, errors: dict) -> None:
        self._errors = errors
        self._path_list = None

    @staticmethod
    def skip_lists(data: Union[dict, list]) -> Any:
        """
        Remove the most external lists from the object.

        Parameters
        ----------
        data : Input data of any type.

        Returns
        -------
        data : Output data of any type without the most external lists.

        """
        while isinstance(data, list):
            if len(data) == 1:
                data = data[0]
            else:
                break

        return data

    def _getitem_skipping_lists(self, error: Union[dict, list], item: Hashable) -> Any:
        """
        Get item from a dictionary.

        """
        return getitem(self.skip_lists(error), item)

    def _get_element_by_path(self, error: Union[dict, list], path: tuple) -> Any:
        """
        Get an element by a path from nested dictionaries.

        """
        return self.skip_lists(
            reduce(self._getitem_skipping_lists, path, self.skip_lists(error))
        )

    def _del_element_by_path(self, error: Union[dict, list], path: tuple) -> None:
        """
        Remove an element by a path from nested dictionaries.

        """
        del self._get_element_by_path(error, path[:-1])[path[-1]]

    def _get_path_to_element(self, error: Union[dict, list]) -> tuple:
        """
        Get a path to an element in nested dictionaries.

        """
        path = list()
        error = self.skip_lists(error)

        while isinstance(error, dict):
            if error == {}:
                break

            key, error = error.popitem()
            error = self.skip_lists(error)
            path.append(key)

        return tuple(path)
