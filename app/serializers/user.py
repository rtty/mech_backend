from app.models import User
from app.serializers.base import BaseSerializer


class UserSerializer(BaseSerializer):
    """
    user serializer
    """

    id = 0
    name = None
    email = None
    role = None
    thumbnailUrl = None

    def __init__(self, user: User) -> None:
        self.id = user.id
        self.name = user.name
        self.email = user.email
        self.role = user.role
        self.thumbnailUrl = user.thumbnail_url
