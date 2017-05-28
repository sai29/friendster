from django.conf.urls import url
from api import views
from rest_framework.authtoken import views as auth_views
urlpatterns = [
		url(r'^api/search/$', views.SearchFriends.as_view(), name="search"),
		url(r'^api/send-request/$', views.SendRequest.as_view()),
		url(r'^api-token-auth/', auth_views.obtain_auth_token),
		url(r'^api/users/$', views.UserCreate.as_view(), name='account-create'),
		url(r'^api/requests/(?P<pk>[0-9]+)/$', views.ConnectionRequestDetail.as_view()),
		url(r'^api/requests/$', views.requests_list),
		url(r'api/friends/$', views.friend_list)
]
