import django_tables2 as tables


from .models import Relation


class RelationTable(tables.Table):

    id = tables.TemplateColumn("<a href='{% url 'relationupdate' record.id %}'>{{ record.id }}</a>")

    description = tables.TemplateColumn("<a href='{% url 'relationdetail' record.id %}'>{{ record }}</a>")
    edit = tables.TemplateColumn("<a href='{% url 'relationupdate' record.id %}'>Edit</a>")
    delete = tables.TemplateColumn("<a href='{% url 'relationdelete' record.id %}'>Delete</a>")

    class Meta:
        model = Relation
        fields = [
            "id",
            "description",
            "edit"
        ]
        sequence = tuple(fields)
        attrs = {"class": "table table-hover table-striped table-condensed"}
