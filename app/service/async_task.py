from typing import Dict, Optional, Union

from django.db.models.query import QuerySet

from app.exceptions.http import HttpException
from app.models import AsyncTask


class AsyncTaskService:
    """
    async task service
    """

    @staticmethod
    def get_async_task(id: int) -> AsyncTask:
        try:
            return AsyncTask.objects.get(pk=id)
        except AsyncTask.DoesNotExist:
            raise HttpException(404, 'Async Task not found')

    @staticmethod
    def create_new_async_task(user_dict):
        return AsyncTask.objects.create(user_id=user_dict.get('id'))

    @staticmethod
    def get_running_tasks() -> QuerySet:
        return AsyncTask.objects.filter(is_running=True)

    @staticmethod
    def cancel_async_task(id: str, user_dict: Dict[str, str]):
        try:
            task = AsyncTask.objects.get(pk=id)
        except AsyncTask.DoesNotExist:
            raise HttpException(404, 'Async Task not found')
        if user_dict.get('role') != 'admin' and user_dict.get('id') != task.user_id:
            raise HttpException(403, "Only task's owner or admin can cancel a running task")
        if not task.is_running:
            raise HttpException(409, 'Task not running')
        task.is_running = False
        task.save()
        return task
