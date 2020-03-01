from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.conf.urls import url

from . import views
from txtbook import views as txtbook_views

app_name = 'txtbook'
urlpatterns = [
    path('', views.index, name='index'),
    path('addtextbook', views.addTextbook, name='addTextbook'),
    path('results/',views.search,name="search"),
    path('textlist',views.textView,name='textlist'),
    path('transfer/<int:pk>',views.transfer,name="transfer"  ),
    path('addexistingtextbook/<int:pk>/',views.addExistingTextbook,name="addExistingTextbook"),
    path('text/<int:pk>/', views.text, name='text'),
    path('allposts', views.allPostsView.as_view(), name='allPosts'),
    path('post/<int:pk>/', views.PostView.as_view(), name='post'),
    path('upload-database',views.textbook_upload,name="textbook_upload"),
    path('logout', views.logout_request, name="logout_request"), # logout request
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
