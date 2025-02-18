"""
This module contains Translator class which translates errors generated by Cerberus to messages defined by a user.

"""

from pathlib import Path
from typing import Union

from cerberus import Validator

from cerberror.errors import ErrConverter
from cerberror.paths import PathFinder


class Translator:
    """
    Translator allows to customize error messages produced by the Cerberus Validator.

    """

    def __init__(self, validator: Validator, path_to_file: Union[str, Path]) -> None:
        """
        Initialize an object and trigger internal computations.

        Parameters
        ----------
        validator : Cerberus object.
        path_to_file : A name of the file storing customized error messages.

        """
        self._validator = validator
        self._path_to_file = Path(path_to_file)
        self._converter = ErrConverter(self._path_to_file)
        self._any_error = False
        self._error_list = list()
        self._paths = None
        self._records = None
        self._errors = dict()

    def _get_paths(self) -> tuple:
        """
        Get paths to all errors produced by Cerberus.

        """
        path_finder = PathFinder(self._validator.errors)
        self._paths = path_finder.paths

        if self._paths == ():
            self._report_error("No path was found")

        return self._paths

    def _get_records(self) -> tuple:
        """
        Get records (paths, err codes, messages) defined by user.

        """
        self._records = self._converter.user_defined_records

        return self._records

    def translate(self, sep: str = " -> ") -> dict:
        """
        Translate errors generated by Cerberus into messages defined by a user.

        Parameters
        ----------
        sep : A string separator between elements in paths. The default is " -> ".

        Returns
        -------
        errors : If success, a result is a dictionary composed of pairs (path to element):(list of errors).
                 Otherwise the returned value is an error container generated by Cerberus originally.

        """
        if self._converter.any_error or self._any_error:
            self._report_error(*self._converter.error_list)
            self._errors = self._validator.errors
        else:
            self._errors = self._translate(sep)

        if self._any_error:
            self._errors = self._validator.errors

        return self._errors

    def _translate(self, sep: str) -> dict:
        """
        Translate errors into defined messages.

        """
        errors = dict()

        for path in self.paths:
            for error in self._validator.document_error_tree.fetch_errors_from(path):
                no_record = False
                for record in self.records:
                    if (error.code in record) and (path in record):
                        no_record = True
                        key = sep.join(map(str, path))

                        if key not in errors:
                            errors.update({key: [self._converter.convert_message(error, record[-1])]})
                        else:
                            errors[key].append(self._converter.convert_message(error, record[-1]))

                if not no_record:
                    self._report_error(
                        f"File '{self._path_to_file}' does not contain a record "
                        f"for path {path} and error code {error.code}"
                    )

        if self._converter.any_error:
            self._report_error(*self._converter.error_list)

        return errors

    def _report_error(self, *errors: str) -> None:
        """
        Notify occurred errors.

        """
        self._any_error = True

        for error in errors:
            self._error_list.append(error)

    @property
    def paths(self) -> tuple:
        """
        Get paths to all elements of Cerberus error contained in nested dictionaries.

        Returns
        -------
        tuple : A list of all paths.

        """
        if (self._paths is None) and (not self._any_error):
            self._get_paths()

        return self._paths

    @property
    def records(self) -> tuple:
        """
        Get records defined by a user in a text file.

        Returns
        -------
        tuple : A list of records. Each record consists of:
                - path to message
                - code of error
                - predefined message

        """
        if (self._records is None) and (not self._any_error):
            self._get_records()

        return self._records

    @property
    def errors(self) -> dict:
        """
        Get converted errors generated by Cerberus.

        Returns
        -------
        dict : A dictionary composed of pairs (path to element):(list of errors) or errors returned by Cerberus.

        """
        return self._errors

    @property
    def any_error(self) -> bool:
        """
        Check whether any error occurred while converting Cerberus's errors.

        Returns
        -------
        bool : False if no errors, otherwise True.

        """
        return self._any_error

    @property
    def error_list(self) -> list:
        """
        Get list of errors which occurred during converting Cerberus's errors into user-defined messages.

        Returns
        -------
        list : List of messages.

        """
        return self._error_list

    @property
    def validator(self) -> Validator:
        """
        Get validator of Cerberus.

        Returns
        -------
        Validator : Cerberus's validator.

        """
        return self._validator

    @validator.setter
    def validator(self, new_validator: Validator) -> None:
        """
        Setter for validator.

        """
        self.__init__(new_validator, self._path_to_file)

    @property
    def path_to_file(self) -> Path:
        """
        Get path to file which stores user defined records.

        Returns
        -------
        Path : path to the file with customized messages.

        """
        return self._path_to_file

    @path_to_file.setter
    def path_to_file(self, new_path_to_file) -> None:
        """
        Setter for path_to_file.

        """
        self.__init__(self._validator, new_path_to_file)
