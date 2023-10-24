from ply.lex import LexToken


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class LexError(Error):
    """Exception raised for errors in the lexer input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class YaccError(Error):
    """Exception raised for errors in the yacc input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class IncompleteRuleError(Error):
    """
    Exception raised for incomplete text errors. i.e. the grammar is OK but the rule is incomplete

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class IncorrectGrammarError(Error):
    """
    Exception raised for incorrect grammar errors. i.e. the grammar is not OK

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression: LexToken, message: str) -> None:
        self.expression = expression
        self.message = message
