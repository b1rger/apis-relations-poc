from itertools import chain

from django import template
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory

from apis_relations2.tables import RelationTable
from apis_relations2.models import Relation
from apis_relations2 import utils
from apis_relations2.forms import RelationForm

register = template.Library()


# For django-tables2 to work we have to pass the request, see https://github.com/jieter/django-tables2/issues/321
# We could also use `uses_context`, but that breaks crispy forms https://github.com/django-crispy-forms/django-crispy-forms/issues/853
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
    return {
            "request": request,
            "instance": instance,
            "table": RelationTable(existing_relations),
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


def is_related(relation: ContentType, model: ContentType) -> bool:
    return relation.model_class().subj_model == model.model_class() or relation.model_class().obj_model == model.model_class()


def relationtypes_with(ct: ContentType) -> list[ContentType]:
    return list(filter(lambda rel: is_related(rel, ct), utils.relation_content_types()))


def contenttype_related_to(ct: ContentType) -> list[ContentType]:
    models = set()
    for rel in relationtypes_with(ct):
        if rel.model_class().obj_model == ct.model_class():
            models.add(rel.model_class().subj_model)
        if rel.model_class().subj_model == ct.model_class():
            models.add(rel.model_class().obj_model)
    return sorted(ContentType.objects.get_for_models(*models).items(), key=lambda item: item[1].name)


@register.simple_tag
def instance_related_to(instance: object) -> list[ContentType]:
    return contenttype_related_to(ContentType.objects.get_for_model(instance))


@register.simple_tag
def all_relations() -> set[ContentType]:
    return utils.relation_content_types()


@register.filter
def contenttypetoclass(ct: ContentType) -> object:
    return ct.model_class()


@register.filter
def modeltocontenttype(model: object) -> ContentType:
    return ContentType.objects.get_for_model(model)


# This is only used in the table, it could be refactored to exist without the filter
@register.filter
def modeltocontenttypename(model: object) -> str:
    return ContentType.objects.get_for_model(model).name
