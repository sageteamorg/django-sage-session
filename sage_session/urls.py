from django.urls import path

from sage_session.views.session import UserSessionsView, DeleteSessionView

urlpatterns = [
    path("user_manage/", UserSessionsView.as_view(), name="usermanagement"),
    path(
        "delete/<str:session_id>/",
        DeleteSessionView.as_view(),
        name="delete_user_session",
    ),
]
