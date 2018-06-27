from django.conf.urls import url
from dashboard import views

urlpatterns = [
    # The home page
    url(r'^$', views.index, name='dashboard'),
    url(r'index', views.index, name='index'),
    url(r'bulletin', views.index, name='bulletin'),

]