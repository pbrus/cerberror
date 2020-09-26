"""
The module contains ErrConverter class replacing Cerberus errors to those defined by a user.

"""
import re
from ast import literal_eval
from pathlib import Path

from cerberus.errors import ValidationError


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
        self._path_to_file = Path(path_to_file)
        self.any_error = False
        self.error_list = list()
        self._user_defined_records = self._read_predefined_messages()

    def _read_predefined_messages(self) -> tuple:
        """
        Read records from a file containing customized errors.

        """
        records = list()

        try:
            with open(self._path_to_file, "r") as file:
                for line in file:
                    record = re.split(
                        r"^\s*([(].*[,].*[)])\s+(\d+)\s+([\"].+[\"])", line.strip()
                    )[1:-1]
                    if record != list():
                        records.append(tuple([i for i in map(literal_eval, record)]))

            if len(records) == 0:
                self._report_error(
                    f"No customized messages have been found in '{self._path_to_file}' file"
                )

        except FileNotFoundError:
            self._report_error(f"File '{self._path_to_file}' does not exist")

        return tuple(records)

    def _report_error(self, error: str) -> None:
        """
        Notify occurred errors.

        """
        self.any_error = True
        self.error_list.append(error)

    def convert_message(self, error: ValidationError, message: str) -> str:
        """
        Convert a predefined message. This method replaces expressions within double curly brackets of a predefined
        message with counterparts from ValidationError class.

        Parameters
        ----------
        error : ValidationError object from Cerberus.
        message : Predefined message defined by a user.

        Returns
        -------
        message : Error message defined by a user. None if an error occurs.

        """
        any_error = False
        attributes = [i.strip("{}") for i in re.findall(r"{{[^{}]+}}", message)]

        for attr in attributes:
            if hasattr(error, attr):
                message = message.replace("{{" + attr + "}}", str(getattr(error, attr)))
            else:
                any_error = True
                self._report_error(
                    f"Invalid expression '{{{{{attr}}}}}' in file '{self._path_to_file}'"
                )

        return message if not any_error else None

    @property
    def user_defined_records(self) -> tuple:
        """
        A property for user defined records.

        Returns
        -------
        tuple : A list of records. Each record consists of:
                - path to message
                - code of error
                - predefined message

        """
        return self._user_defined_records
