import uuid
from typing import Dict, Optional, Union

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from app.exceptions.http import HttpException
from app.models import Invitation, User, Workspace
from app.service.workspace import WorkspaceService
from app.utils import helper


class InvitationService:
    """
    invitation service
    create_new_invitation(): create a new invitation
    accept_invitation(): accept an invitation and join a workspace
    """

    def create_new_invitation(
        self,
        user_data: Dict[str, Optional[Union[str, int]]],
        data: Dict[str, Union[int, str]],
    ):
        email = data.get('email')
        workspace_id = data.get('workspaceId')

        if email is None:
            raise HttpException(400, 'Email field is required')

        try:
            validate_email(email)
        except ValidationError:
            raise HttpException(400, 'Invalid email')

        subject = 'Mechanics Invitation'
        email_from = settings.EMAIL_FROM
        if email_from is None:
            raise HttpException(500, 'EMAIL_FROM not configured')

        if workspace_id is None:
            url = settings.GENERAL_INVITATION_URL
            html = render_to_string('invitation_without_workspace.html', dict(url=url))
        else:
            helper.check_int('workspaceId field', workspace_id)
            try:
                workspace = Workspace.objects.get(pk=workspace_id)
                if user_data.get('role') != 'admin' and workspace.user_id != user_data.get('id'):
                    raise HttpException(
                        403,
                        'Only owner or super user can invite another user to a workspace',
                    )
                user = User.objects.get(email=email)
                invitation = Invitation.objects.create(user=user, workspace=workspace)
                url = settings.WORKSPACE_INVITATION_URL.replace('<token>', str(invitation.token))
                html = render_to_string(
                    'invitation_with_workspace.html',
                    dict(url=url, workspace=workspace.name),
                )
            except Workspace.DoesNotExist:
                raise HttpException(400, 'Workspace not found')
            except User.DoesNotExist:
                raise HttpException(400, 'No user with that email found')

        text = strip_tags(html)
        msg = EmailMultiAlternatives(subject, text, email_from, [email])
        msg.attach_alternative(html, 'text/html')
        msg.send()

    def accept_invitation(
        self, user_data: Dict[str, Optional[Union[str, int]]], data: Dict[str, str]
    ):
        user_id = user_data.get('id')
        token = data.get('token')
        helper.check_token('token field', token)
        try:
            invitation = Invitation.objects.get(user_id=user_id, token=uuid.UUID(token))
            invitation.accept()
            WorkspaceService().add_members(invitation.workspace_id, user_id)
        except Invitation.DoesNotExist:
            raise HttpException(403, 'There is no invitation matching that token')
