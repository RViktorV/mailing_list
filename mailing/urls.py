from django.urls import path
from .views import ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView, MessageListView, \
    MessageCreateView, MessageUpdateView, MessageDeleteView, MailingListView, MailingCreateView, MailingUpdateView, \
    MailingDeleteView, AttemptListView, home
from mailing.apps import MailingConfig

app_name = MailingConfig.name

urlpatterns = [
    path('', home, name='home'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),
    path('message/', MessageListView.as_view(), name='message-list'),
    path('message/create/', MessageCreateView.as_view(), name='message-create'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),
    path('mailings/', MailingListView.as_view(), name='mailing-list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing-create'),
    path('mailings/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing-update'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing-delete'),
    path('attempt/', AttemptListView.as_view(), name='attempt-list'),

]
