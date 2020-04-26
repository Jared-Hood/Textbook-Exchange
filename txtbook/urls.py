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
    path('homepage',views.homepage,name='homepage'),
    path('addtextbook', views.addTextbook, name='addTextbook'),
    path('results/',views.search,name="search"),
    path('textlist',views.textView,name='textlist'),
    path('transfer/<int:pk>',views.transfer,name="transfer"  ),
    path('addexistingtextbook/<int:pk>/',views.addExistingTextbook,name="addExistingTextbook"),
    path('text/<int:pk>/', views.text, name='text'),
    # path('allposts', views.allPosts, name='allPosts'),
    path('allposts', views.allPostsView.as_view(), name='allPosts'),
    path('post/<int:pk>/', views.PostView.as_view(), name='post'),
    path('upload-database',views.textbook_upload,name="textbook_upload"),
    path('logout', views.logout_request, name="logout_request"), # logout request
    path('filtered_posts_search/',views.filtered_posts_search,name="filtered_posts_search"),
    path('contactSeller/<int:pk>', views.contactSeller, name='contactSeller'),
    path('contactSeller/<int:pk>/sent', views.sendEmail, name='sendEmail'),
    path('profile_page/<int:pk>',views.profile_page.as_view(), name="profile_page"),
    path('create_profile',views.create_profile,name="create_profile"),
    path('<int:pk>/edit_profile',views.edit_profile,name="edit_profile"),
    path('posts/<int:pk>/', views.search_posts_by_book, name="search_posts"),
    path('<int:pk>/edit_post_database_text',views.edit_post_database_text,name="edit_post_database_text"),
    path('<int:pk>/edit_post_original_text',views.edit_post_original_text,name="edit_post_original_text"),
    path('<int:profile_pk>/<int:post_pk>/delete_post',views.delete_post,name="delete_post"),
    path('<int:pk>/mark_post_sold',views.mark_post_sold,name="mark_post_sold"),
    path('<int:pk>/repost',views.repost,name="repost"),
    path('search_by_class/', views.class_search_view, name="search_by_class"),
    path('search_by_class/results', views.search_by_class, name='class_search'),
    path('search_options', views.search_options, name="search_options"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
