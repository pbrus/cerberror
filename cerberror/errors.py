"""
The module contains ErrConverter class replacing Cerberus errors to those defined by a user.

"""
import re
from ast import literal_eval

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
        self._path_to_file = path_to_file
        self._any_error = False
        self._error_list = list()
        self._predefined_messages = self._read_predefined_messages()

    def _read_predefined_messages(self) -> tuple:
        """
        Read records from a file containing customized errors.

        """
        messages = list()

        try:
            with open(self._path_to_file, "r") as file:
                for line in file:
                    record = re.split(
                        r"^\s*([(].*[,].*[)])\s+(\d+)\s+([\"].+[\"])", line.strip()
                    )[1:-1]
                    if record != list():
                        messages.append(tuple([i for i in map(literal_eval, record)]))

            if len(messages) == 0:
                self._report_error(
                    f"No customized messages have been found in '{self._path_to_file}' file"
                )

        except FileNotFoundError:
            self._report_error(f"File '{self._path_to_file}' does not exist")

        return tuple(messages)

    def _report_error(self, error: str) -> None:
        """
        Notify occurred errors.

        """
        self._any_error = True
        self._error_list.append(error)

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
        attributes = [i.strip("{}") for i in re.findall(r"{{[^{}]+}}", message)]

        for attr in attributes:
            if hasattr(error, attr):
                message = message.replace("{{" + attr + "}}", str(getattr(error, attr)))
            else:
                self._report_error(
                    f"Invalid expression '{{{{{attr}}}}}' in file '{self._path_to_file}'"
                )

        if self._any_error:
            message = None

        return message
