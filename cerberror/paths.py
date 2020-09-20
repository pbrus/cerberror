"""
The module contains PathFinder class which goes through dictionary of errors and gets all paths to elements.

"""
from copy import deepcopy
from functools import reduce
from operator import getitem
from typing import Any, Hashable, Union


class PathFinder:
    """
    PathFinder walks through error's dictionary and gets sequences of keys to all elements.

    """

    def __init__(self, errors: dict) -> None:
        """
        Initialize an object.

        Parameters
        ----------
        errors : Errors dictionary produced by Cerberus.

        """
        self._errors = errors
        self._paths_list = list()

    @staticmethod
    def skip_lists(data: Union[dict, list]) -> Any:
        """
        Remove the most external lists from the object.

        Parameters
        ----------
        data : Input data, may be a dictionary or a list.

        Returns
        -------
        data : Output data without the most external lists.

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

    def get_paths(self) -> tuple:
        """
        Get paths to all elements of error nested dictionaries.

        Returns
        -------
        tuple : A list of all paths. Each path is represented by a tuple consisting a sequence of keys.

        """
        errors = deepcopy(self._errors)
        temp_errors = deepcopy(self._errors)

        while temp_errors != {}:
            path = self._get_path_to_element(temp_errors)

            if self._get_element_by_path(errors, path) != {}:
                self._paths_list.append(path)

            self._del_element_by_path(errors, path)
            temp_errors = deepcopy(errors)

        return tuple(self._paths_list)

    @property
    def paths(self) -> Union[tuple, list]:
        """
        Property of a list with all paths coming from an error dictionary.

        Returns
        -------
        tuple : A list of all paths.

        """
        return self._paths_list
