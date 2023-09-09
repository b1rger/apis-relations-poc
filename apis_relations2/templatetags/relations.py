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


@register.simple_tag
def relations_table(instance, contenttype=None):
    """
    List all relations that go from an instance to a contenttype.
    If no instance is passed, it lists all relations to a contenttype.
    If neither instance nor contenttype are passed, it lists all relations.
    All those lists can include different kinds of relations!
    """
    model = None
    cssid = "table"
    existing_relations = list()

    if contenttype:
        model = contenttype.model_class()
        cssid = f"{contenttype.model}_table"

    # special case: when the contenttype is the same as the contenttype of
    # the instance, we don't want *all* the relations where the instance
    # occurs, but only those where it occurs together with another of its
    # type
    if ContentType.objects.get_for_model(instance) == contenttype:
        relation_types = utils.relation_content_types(combination=(model, model))
    else:
        relation_types = utils.relation_content_types(any_model=model)

    for rel in relation_types:
        if instance:
            existing_relations.extend(list(rel.model_class().objects.filter(Q(subj=instance)|Q(obj=instance))))
        else:
            existing_relations.extend(list(rel.model_class().objects.all()))

    table = RelationTable
    if model:
        table = table_factory(model, RelationTable)
    return table(existing_relations, attrs={"id": cssid})


@register.inclusion_tag("partials/relations_links.html")
def relations_links(instance=None, contenttype=None):
    tomodel = None
    if contenttype:
        tomodel = contenttype.model_class()

    frommodel = None
    if instance:
        frommodel = type(instance)

    return {
        "relation_types": [(ct, ct.model_class()) for ct in utils.relation_content_types(combination=(frommodel, tomodel))],
        "relation_types_reverse": utils.relation_content_types(subj_model=tomodel, obj_model=frommodel),
        "instance": instance,
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
def relations_css() -> str:
    cssfile = static("relations.css")
    return format_html('<link rel="stylesheet" href="{}">', cssfile)
