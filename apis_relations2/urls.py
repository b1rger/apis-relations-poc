from django.urls import path
from . import views

app_name = 'apis_relations2'

urlpatterns = [
        path('relations/all', views.RelationsList.as_view(), name='relations'),
        path('relationtype/<int:contenttype>', views.RelationType.as_view(), name='relationtype'),
        path('relationtype/<int:contenttype>/<int:fromsubj>', views.RelationType.as_view(), name='relationtypefrom'),
        path('relationtype/<int:contenttype>/<int:fromsubj>/partial', views.RelationCreateViewPartial.as_view(), name='relationcreatefrompartial'),
        path('relationtype/<int:contenttype>/<int:fromsubj>/tablepartial', views.RelationTablePartial.as_view(), name='relationtablepartial'),
        path('relation/<int:pk>/update', views.RelationUpdate.as_view(), name='relationupdate'),
        path('relation/<int:pk>/delete', views.RelationDelete.as_view(), name='relationdelete'),
        # won't probably need this one
        path('relation/<int:pk>/detail', views.RelationDetail.as_view(), name='relationdetail'),
]
