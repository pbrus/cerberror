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

    @staticmethod
    def _getitem_skipping_lists(error: Union[dict, list], item: Hashable) -> Any:
        """
        Get item from a dictionary.

        """
        return getitem(PathFinder.skip_lists(error), item)

    @staticmethod
    def _get_element_by_path(error: Union[dict, list], path: tuple) -> Any:
        """
        Get element by path from a nested dictionaries.

        """
        return PathFinder.skip_lists(
            reduce(
                PathFinder._getitem_skipping_lists, path, PathFinder.skip_lists(error)
            )
        )

    @staticmethod
    def _del_element_by_path(error: Union[dict, list], path: tuple) -> None:
        """
        Remove element by path from a nested dictionaries.

        """
        del PathFinder._get_element_by_path(error, path[:-1])[path[-1]]
