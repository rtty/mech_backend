import asyncio
from typing import Callable

from asgiref.sync import async_to_sync, sync_to_async
from django.core.files.uploadedfile import (InMemoryUploadedFile,
                                            SimpleUploadedFile)
from django.urls import reverse
from django.utils.decorators import classonlymethod
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.async_task import AsyncTaskSerializer
from app.serializers.rule import RuleSerializer
from app.serializers.status import StatusSerializer
from app.serializers.test import TestSerializer
from app.service.async_task import AsyncTaskService
from app.service.file_import import FileImportService


class FileImportApi(BaseAPI, generics.CreateAPIView):
    parser_classes = [MultiPartParser]

    @classonlymethod
    def as_view(cls, **initkwargs) -> Callable:
        view = super().as_view(**initkwargs)
        view._iscoroutine = asyncio.coroutines.iscoroutine
        return view

    @async_to_sync
    async def post(self, request, *args, **kwargs):
        return await self.create(request, *args, **kwargs)

    @staticmethod
    def __create(request, filename, current_user, loop):
        if filename == 'rule':
            rule = FileImportService().import_rule(request.data.get('file'), current_user)
            return Response(RuleSerializer(rule).to_dict(), status=status.HTTP_201_CREATED)

        elif filename == 'project':
            running = AsyncTaskService().get_running_tasks()
            if len(running):
                raise HttpException(
                    409,
                    'Another tasks already running: {}'.format(
                        list(running.values_list('pk', flat=True))
                    ),
                )

            file = request.data.get('file')
            if isinstance(file, InMemoryUploadedFile):
                # Clone a new file for InMemoryUploadedFile.
                # Because the old one will be closed by Django.
                file = SimpleUploadedFile(file.name, file.read(), file.content_type)

            task = AsyncTaskService().create_new_async_task(current_user)
            loop.create_task(
                sync_to_async(FileImportService().import_project)(file, task_id=task.pk)
            )

            return Response(
                AsyncTaskSerializer(task).to_dict(),
                status=status.HTTP_202_ACCEPTED,
                headers={'location': reverse('retrieve-async-task', args=[task.pk])},
            )
        elif filename == 'mappings':
            tests = FileImportService().import_mappings(request.data.get('file'), current_user)
            return Response(
                list(map(lambda p: TestSerializer(p).to_dict(), tests)),
                status=status.HTTP_201_CREATED,
            )
        else:
            raise HttpException(404, 'Unknown resource type: ' + filename)

    async def create(self, request: Request, filename: str) -> Response:
        try:
            current_user = await sync_to_async(self.check_user_token)(request)
            if current_user.get('role') != 'admin':
                raise HttpException(403, 'Only Admin users are allowed')
            if request.data.get('file') is None:
                raise HttpException(400, 'No file uploaded')
            loop = asyncio.get_event_loop()
            return await sync_to_async(self.__create)(request, filename, current_user, loop)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
