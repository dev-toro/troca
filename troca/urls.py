from django.conf.urls import patterns, include, url
from django.contrib import admin
from core.views import Home, Project_view, AboutView, OurPeople, Create_skill, Edit_project, Profile, Category_view, Category_view_filter, Sub_category_view_filter, Users_view, Settings, Create_project, Register, Login, Create_profile, Trueques
from core import views
from django.conf import settings
from django.contrib.auth.decorators import login_required


urlpatterns = patterns(
    '',
    url(r'^likes/', include('phileo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', Home.as_view(), name='index'),
    url(r'^proyecto/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', Project_view.as_view(), name='project'),
    url(r'^proyecto/editar/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', Edit_project.as_view(), name='editproject'),
    url(r'^perfil/(?P<slug>[-_\w]+)/$', Profile.as_view(), name='profile'),
    url(r'^descubre/$', Category_view.as_view() , name='category'),
    url(r'^descubre/(?P<category>\w+)/$', Category_view_filter.as_view(), name='subcategory'),
    url(r'^descubre/(?P<category>\w+)/(?P<subcategory>\w+)/$', Sub_category_view_filter.as_view(), name='detailsubcategory'),
    url(r'^encuentra/$', Users_view.as_view() , name='encuentra'),
    url(r'^register/$', Register.as_view(), name='register'), 
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^register/perfil/$', Create_profile.as_view(), name='createprofile'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^configuracion/(?P<username>\w+)/$', login_required(Settings.as_view()), name='settings'),
    url(r'^crea/$', login_required(Create_project.as_view()), name='create'),
    url(r'^crea/habilidad/$', login_required(Create_skill.as_view()), name='createSkill'),
    url(r'^froala_editor/', include('froala_editor.urls')),
    url(r'^mensajes/', include('postman.urls')),
    url(r'^colaborar/(?P<username>\w+)/(?P<slug>[-_\w]+)/$', login_required(views.register_collaborator), name='collaborate'),
    url(r'^colaboraciones/(?P<username>\w+)/$', login_required(Trueques.as_view()), name='trueques'),
    url(r'^colaboraciones/eliminar/(?P<username>\w+)/$', views.Del_trueque, name='elimTrueque'),
    url(r'^acerca_de_troca$', AboutView.as_view(), name='about'),
    url(r'^quienes_somos', OurPeople.as_view(), name='ourpeople'),
)


if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )

