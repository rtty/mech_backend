from app.serializers.base import BaseSerializer


class StatusSerializer(BaseSerializer):
    """
    status serializer
    """

    code = 0
    message = None

    def __init__(self, code, message):
        self.code = code
        self.message = message
