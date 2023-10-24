from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.service.invitation import InvitationService


class InvitationAPI(BaseAPI, generics.CreateAPIView):
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Invite a user to a workspace
        """
        try:
            current_user = self.check_user_token(request)
            InvitationService().create_new_invitation(current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # Success
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request: Request, *args, **kwargs) -> Response:
        """
        Accept an invitation
        """
        try:
            current_user = self.check_user_token(request)
            InvitationService().accept_invitation(current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # Success
        return Response(status=status.HTTP_204_NO_CONTENT)
