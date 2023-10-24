from rest_framework import status


class HttpException(Exception):
    """
    Http exceptions
    """

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def get_http_status(self) -> int:
        """
        Get http status by code

        :return: http status
        """
        if self.code == 400:
            http_status = status.HTTP_400_BAD_REQUEST
        elif self.code == 401:
            http_status = status.HTTP_401_UNAUTHORIZED
        elif self.code == 403:
            http_status = status.HTTP_403_FORBIDDEN
        elif self.code == 404:
            http_status = status.HTTP_404_NOT_FOUND
        elif self.code == 409:
            http_status = status.HTTP_409_CONFLICT
        else:
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return http_status
