import django_tables2 as tables

from django.contrib.contenttypes.models import ContentType

from .models import Relation


class RelationTable(tables.Table):

    id = tables.TemplateColumn("<a href='{% url 'relationupdate' record.id %}'>{{ record.id }}</a>")

    description = tables.TemplateColumn("{{ record }}")
    edit = tables.TemplateColumn("<a href='{% url 'relationupdate' record.id %}'>Edit</a>")
    delete = tables.TemplateColumn("{% load relations %}{% with record|modeltocontenttype as ct %}<a href='{% url 'relationdelete' record.id %}?next={{request.path}}' hx-post='{% url 'relationdelete' record.id %}?next={% url 'relationpartial' ct.id record.subj.id %}?success' hx-target='#{{record.obj_model|modeltocontenttypename}}_table' hx-confirm='Are your sure you want to delete {{ record }}?'>Delete</a>{% endwith %}")

    class Meta:
        model = Relation
        fields = [
            "id",
            "description",
            "edit"
        ]
        sequence = tuple(fields)
        attrs = {"class": "table table-hover table-striped table-condensed"}
