from django.urls import path

from . import views
from txtbook import views as txtbook_views

app_name = 'txtbook'
urlpatterns = [
    path('', views.index, name='index'),
    path('addtextbook', views.addTextbook, name='addTextbook'),
    path('results/',views.search,name="search"),
    # path('allposts', views.allPosts, name='allPosts'),
    path('transfer/<int:pk>',views.transfer,name="transfer"  ),
    path('addexistingtextbook/<int:pk>/',views.addExistingTextbook,name="addExistingTextbook"),
    path('text/<int:pk>/', views.TextView, name='text'),
    path('allposts', views.allPostsView.as_view(), name='allPosts'),
    path('post/<int:pk>/', views.PostView.as_view(), name='post'),
    path('upload-database',views.textbook_upload,name="textbook_upload"),
]
