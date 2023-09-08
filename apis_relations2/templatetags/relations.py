from itertools import chain

from django import template
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.templatetags.static import static
from django.utils.html import format_html
from django_tables2.tables import table_factory

from apis_relations2.tables import RelationTable
from apis_relations2.models import Relation
from apis_relations2 import utils
from apis_relations2.forms import RelationForm

register = template.Library()


# For django-tables2 to work we have to pass the request, see https://github.com/jieter/django-tables2/issues/321
@register.inclusion_tag("partials/relations_table.html")
def relations_table(request, instance=None, contenttype=None):
    model = None
    if contenttype:
        model = contenttype.model_class()

    relation_types = utils.relation_content_types(any_model=model)
    existing_relations = list()

    for rel in relation_types:
        if instance:
            existing_relations.extend(list(rel.model_class().objects.filter(Q(subj=instance)|Q(obj=instance))))
        else:
            existing_relations.extend(list(rel.model_class().objects.all()))

    table = RelationTable
    if model:
        table = table_factory(model, RelationTable)
    return {
            "request": request,
            "instance": instance,
            "table": table(existing_relations),
            "contenttype": contenttype,
    }


@register.inclusion_tag("partials/relations_links.html")
def relations_links(instance=None, contenttype=None, collapse=True, htmx=True, next=None):
    tomodel = None
    if contenttype:
        tomodel = contenttype.model_class()

    frommodel = None
    if instance:
        frommodel = type(instance)

    return {
        "relation_types": utils.relation_content_types(combination=(frommodel, tomodel)),
        "relation_types_reverse": utils.relation_content_types(subj_model=tomodel, obj_model=frommodel),
        "instance": instance,
        "collapse": collapse,
        "htmx": htmx,
        "next": next,
    }


@register.simple_tag
def relation_form(relation: ContentType, instance=None):
    initial = {}
    if instance:
        initial['subj'] = instance
    exclude = []
    return modelform_factory(relation.model_class(), form=RelationForm, exclude=exclude)(initial=initial)


def contenttype_can_be_related_to(ct: ContentType) -> list[ContentType]:
    models = set()
    for rel in utils.relation_content_types(any_model=ct.model_class()):
        models.add(rel.model_class().subj_model)
        models.add(rel.model_class().obj_model)
    contenttypes = ContentType.objects.get_for_models(*models)
    models = sorted(contenttypes.items(), key=lambda item: item[1].name)
    return [item[1] for item in models]


@register.simple_tag
def instance_can_be_related_to(instance: object) -> list[ContentType]:
    return contenttype_can_be_related_to(ContentType.objects.get_for_model(instance))


@register.simple_tag
def instance_is_related_to(instance: object) -> list[ContentType]:
    models = set()
    for rel in Relation.objects.filter(subj=instance).select_subclasses():
        models.add(rel.obj_model)
    for rel in Relation.objects.filter(obj=instance).select_subclasses():
        models.add(rel.subj_model)
    contenttypes = ContentType.objects.get_for_models(*models)
    models = sorted(contenttypes.items(), key=lambda item: item[1].name)
    return [item[1] for item in models]


@register.simple_tag
def all_relations() -> set[ContentType]:
    return utils.relation_content_types()


@register.filter
def contenttypetoclass(ct: ContentType) -> object:
    return ct.model_class()


@register.filter
def modeltocontenttype(model: object) -> ContentType:
    return ContentType.objects.get_for_model(model)


@register.simple_tag
def relations_css() -> str:
    cssfile = static("relations.css")
    return format_html('<link rel="stylesheet" href="{}">', cssfile)
