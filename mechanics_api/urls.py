"""
Api URL Configuration
"""
from django.urls import path

from app.controllers.async_task import (
    AsyncTaskCancelAPI, AsyncTaskDetailAPI, AsyncTaskListAPI)
from app.controllers.file_import import FileImportApi
from app.controllers.invitation import InvitationAPI
from app.controllers.node_function import NodeFunctionAPI
from app.controllers.project import ProjectDetailAPI, ProjectListAPI
from app.controllers.rule import RuleCopyAPI, RuleDetailAPI, RuleListAPI
from app.controllers.rule_function import RuleFunctionAPI
from app.controllers.rule_version import (RuleVersionDetailAPI,
                                          RuleVersionListAPI,
                                          RuleVersionModifyAPI,
                                          RuleVersionNodeDetailAPI,
                                          RuleVersionNodeModifyAPI,
                                          RuleVersionNodeNotesDetailAPI,
                                          RuleVersionTestsAPI)
from app.controllers.test import TestAPI, TestListAPI
from app.controllers.test_category import (TestCategoryAPI,
                                           TestCategoryListAPI,
                                           TestCategoryWithTestListAPI)
from app.controllers.user import UserDetailAPI, UserListAPI, UserRoleAPI
from app.controllers.workspace import (WorkspaceCopyAPI, WorkspaceDetailAPI,
                                       WorkspaceListAPI)

urlpatterns = [
    path('api/v1/users', UserListAPI.as_view()),
    path('api/v1/users/<id>', UserDetailAPI.as_view()),
    path('api/v1/users/<id>/role', UserRoleAPI.as_view()),
    path('api/v1/workspaces', WorkspaceListAPI.as_view()),
    path('api/v1/workspaces/<id>', WorkspaceDetailAPI.as_view()),
    path('api/v1/workspaces/<id>/copy', WorkspaceCopyAPI.as_view()),
    path('api/v1/rules', RuleListAPI.as_view()),
    path('api/v1/rules/<id>', RuleDetailAPI.as_view()),
    path('api/v1/rules/<id>/copy', RuleCopyAPI.as_view()),
    path('api/v1/rules/<id>/rule-versions', RuleVersionListAPI.as_view()),
    path('api/v1/rule-versions/<id>', RuleVersionDetailAPI.as_view()),
    path('api/v1/rule-versions/<id>/nodes/notes', RuleVersionNodeNotesDetailAPI.as_view()),
    path('api/v1/rule-versions/<id>/<modify_type>', RuleVersionModifyAPI.as_view()),
    path('api/v1/rule-versions/<id>/nodes/<node_id>', RuleVersionNodeDetailAPI.as_view()),
    path(
        'api/v1/rule-versions/<id>/nodes/<node_id>/<modify_type>',
        RuleVersionNodeModifyAPI.as_view(),
    ),
    path('api/v1/rule-versions/<id>/tests/<test_id>', RuleVersionTestsAPI.as_view()),
    path('api/v1/projects', ProjectListAPI.as_view()),
    path('api/v1/projects/<id>', ProjectDetailAPI.as_view()),
    path('api/v1/rules/functions/<function>', RuleFunctionAPI.as_view()),
    path('api/v1/rules/node-functions/<function>', NodeFunctionAPI.as_view()),
    path('api/v1/invitations', InvitationAPI.as_view()),
    path('api/v1/import/<filename>', FileImportApi.as_view()),
    path(
        'api/v1/async-tasks/running',
        AsyncTaskListAPI.as_view(),
        name='list-running-tasks',
    ),
    path(
        'api/v1/async-tasks/<id>',
        AsyncTaskDetailAPI.as_view(),
        name='retrieve-async-task',
    ),
    path('api/v1/async-tasks/<id>/cancel', AsyncTaskCancelAPI.as_view()),
    path('api/v1/mappings', TestCategoryWithTestListAPI.as_view()),
    path('api/v1/mappings/test-categories', TestCategoryListAPI.as_view()),
    path('api/v1/mappings/test-categories/<id>', TestCategoryAPI.as_view()),
    path('api/v1/mappings/tests', TestListAPI.as_view()),
    path('api/v1/mappings/tests/<id>', TestAPI.as_view()),
]

