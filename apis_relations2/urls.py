from django.urls import path
from . import views

app_name = 'apis_relations2'

urlpatterns = [
        path('relations/all', views.RelationsList.as_view(), name='relations'),

        path('relations/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>', views.RelationsListPartial.as_view(), name='relations'),
        path('relations/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>/<int:tocontenttype>', views.RelationsListPartial.as_view(), name='relations'),

        path('relationtype/<int:contenttype>', views.RelationView.as_view(), name='relation'),
        path('relationtype/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>/<int:tocontenttype>', views.RelationView.as_view(), name='relation'),
        path('relationtype/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>/<int:tocontenttype>/inverted', views.RelationView.as_view(inverted=True), name='relationinverted'),

        path('relationtype/<int:contenttype>/partial', views.RelationViewPartialFormOnly.as_view(), name='relationpartial'),
        path('relationtype/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>/<int:tocontenttype>/partial', views.RelationViewPartialFormOnly.as_view(), name='relationpartial'),
        path('relationtype/<int:contenttype>/<int:fromcontenttype>/<int:fromoid>/<int:tocontenttype>/partial/inverted', views.RelationViewPartialFormOnly.as_view(inverted=True), name='relationpartialinverted'),

        path('relation/<int:pk>/update', views.RelationUpdate.as_view(), name='relationupdate'),
        path('relation/<int:pk>/delete', views.RelationDelete.as_view(), name='relationdelete'),
]
