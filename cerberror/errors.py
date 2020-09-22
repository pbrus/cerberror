"""
The module contains ErrConverter class replacing Cerberus errors to those defined by a user.

"""
import re
from ast import literal_eval


class ErrConverter:
    """
    ErrConverter converts errors produced by Cerberus to customized messages.

    """

    def __init__(self, path_to_file: str) -> None:
        """
        Initialize an object.

        Parameters
        ----------
        path_to_file : A name of the file storing customized error messages.

        """
        self._path_to_file = path_to_file
        self._any_error = False
        self._error_list = list()

    def _read_messages(self) -> tuple:
        """
        Read records from a file containing customized errors.

        """
        messages = list()

        try:
            with open(self._path_to_file, "r") as file:
                for line in file:
                    record = re.split(r"^\s*([(].*[,].*[)])\s+(\d+)\s+([\"].+[\"])", line.strip())[1:-1]
                    if record != list():
                        messages.append(tuple([i for i in map(literal_eval, record)]))
        except FileNotFoundError:
            self._report_error(f"File '{self._path_to_file}' does not exist")

        return tuple(messages)

    def _report_error(self, error: str) -> None:
        """
        Notify occurred errors.

        """
        self._any_error = True
        self._error_list.append(error)
