from django.conf.urls import url
from dashboard import views

urlpatterns = [
    # The home page
    url(r'^$', views.index, name='dashboard'),
]