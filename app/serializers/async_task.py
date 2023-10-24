from app.models import AsyncTask
from app.serializers.base import BaseSerializer


class AsyncTaskSerializer(BaseSerializer):
    """
    Async task serializer
    """

    id = 0
    dateCreated = None
    userId = 0
    progress = 0
    isRunning = False
    result = None

    def __init__(self, task: AsyncTask):
        self.id = task.id
        self.dateCreated = task.date_created
        self.userId = task.user_id
        self.progress = task.progress
        self.isRunning = task.is_running
        if not task.is_running:
            self.result = task.result
