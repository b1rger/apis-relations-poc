from django.urls import path
from . import views

app_name = 'apis_relations2'

urlpatterns = [
        path('relations/all', views.RelationsList.as_view(), name='relations'),
        path('relationtype/<int:contenttype>', views.RelationView.as_view(), name='relation'),
        path('relationtype/<int:contenttype>/<int:fromsubj>', views.RelationView.as_view(), name='relation'),
        path('relationtype/<int:contenttype>/<int:fromsubj>/reversed', views.RelationView.as_view(reversed=True), name='relationreversed'),

        path('relationtype/<int:contenttype>/partial', views.RelationViewPartial.as_view(), name='relationpartial'),
        path('relationtype/<int:contenttype>/<int:fromsubj>/partial', views.RelationViewPartial.as_view(), name='relationpartial'),
        path('relationtype/<int:contenttype>/<int:fromsubj>/partial/reversed', views.RelationViewPartial.as_view(reversed=True), name='relationpartialreversed'),

        path('relation/<int:pk>/update', views.RelationUpdate.as_view(), name='relationupdate'),
        path('relation/<int:pk>/delete', views.RelationDelete.as_view(), name='relationdelete'),
]
