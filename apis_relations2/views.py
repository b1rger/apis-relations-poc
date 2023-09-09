from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView, ProcessFormView, FormMixin, ProcessFormView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.urls import reverse
from django.http import Http404, HttpResponse

from django_tables2 import SingleTableView, SingleTableMixin

from .models import Relation
from .forms import RelationForm
from .utils import relation_content_types
from .tables import RelationTable
from .templatetags import relations


class RelationsList(SingleTableView):
    """
    List all available relations
    Using the `relations_links` templatetag, the `relations_list.html` template
    also lists all existing relation types on top of the relation list.
    """
    template_name = "relations_list.html"
    table_class = RelationTable
    model = Relation

    def get_queryset(self):
        return super().get_queryset().select_subclasses()


class RelationsListPartial(TemplateView):
    """
    List relations going away from an instance. In case the `tocontenttype` is
    passed, the relations are limited to those that point to this contenttype
    This is only used in a partial template to provide a response to htmx
    requests that add relations.
    """
    template_name = "partial.html"

    def get_context_data(self, *args, **kwargs):
        fromcontenttype = ContentType.objects.get_for_id(kwargs.get("fromcontenttype"))
        frominstance = fromcontenttype.get_object_for_this_type(pk=kwargs.get("fromoid"))
        if tocontenttype := kwargs.get("tocontenttype"):
            tocontenttype = ContentType.objects.get_for_id(tocontenttype)
        ctx = super().get_context_data()
        ctx["table"] = relations.relations_table(frominstance, tocontenttype)
        return ctx


################################################
# Views working with a specific Relation type: #
################################################

class RelationMixin:
    """
    This mixin checks if the relation really
    exists and returns 404 if it does not.
    """
    frominstance = None

    def dispatch(self, request, *args, **kwargs):
        # basic check before anything else: lookup the contenttype and see if we
        # are really working with a relation content type
        self.contenttype = ContentType.objects.get_for_id(kwargs.get("contenttype"))
        if self.contenttype not in relation_content_types():
            raise Http404(f"Relation with id {kwargs['contenttype']} does not exist")
        if fromoid := self.kwargs.get("fromoid"):
            if fromcontenttype := self.kwargs.get("fromcontenttype"):
                self.frominstance = ContentType.objects.get_for_id(fromcontenttype).get_object_for_this_type(pk=fromoid)
        return super().dispatch(request, *args, **kwargs)


class RelationViewPartialFormOnly(RelationMixin, CreateView):
    """
    A partial view providing a form for creating new relations.
    This form is embedded into views using htmx
    """
    template_name = "partial.html"
    inverted = False

    def get_form_class(self):
        return modelform_factory(self.contenttype.model_class(), form=RelationForm, exclude=[])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # we set pass `hxnext` to the form, which then uses this value to add this
        # to the hx-post URL as `hx-next` - our view redirects to this path to let
        # the htmx request get the correct results
        kwargs["hxnext"] = reverse("relations", kwargs=self.request.resolver_match.kwargs)

        if self.frominstance:
            fromcontenttype = ContentType.objects.get_for_model(self.frominstance).pk
            tocontenttype = ContentType.objects.get_for_id(self.kwargs.get("tocontenttype"))
            hxnextargs = [fromcontenttype, self.frominstance.pk, tocontenttype]
            kwargs["frominstance"] = self.frominstance
            kwargs["tocontenttype"] = tocontenttype

        kwargs["inverted"] = self.inverted
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['model'] = self.contenttype.model_class()
        return ctx

    def get_success_url(self):
        if hxnext := self.request.GET.get("hx-next"):
            return hxnext
        args = [self.contenttype.id,]
        if fromsubj := self.kwargs.get("fromsubj"):
            args.append(fromsubj)
        if self.inverted:
            return reverse("relationinverted", args=args)
        return reverse("relation", args=args)


# This should/could be combined with  RelationsListPartial
class RelationView(RelationViewPartialFormOnly):
    """
    A view that provides both a list of relations *and* a form for
    creating new relations
    """
    template_name = "relations_list.html"

    def get_context_data(self, *args, **kwargs):
        fromcontenttype = ContentType.objects.get_for_id(self.kwargs.get("fromcontenttype"))
        frominstance = fromcontenttype.get_object_for_this_type(pk=self.kwargs.get("fromoid"))
        if tocontenttype := self.kwargs.get("tocontenttype"):
            tocontenttype = ContentType.objects.get_for_id(tocontenttype)
        ctx = super().get_context_data()
        ctx["table"] = relations.relations_table(frominstance, tocontenttype)
        return ctx

#################################################
# Views working with single Relation instances: #
#################################################

class RelationUpdate(UpdateView):
    template_name = "relations_list.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["embedded"] = False
        return kwargs

    def get_form_class(self):
        return modelform_factory(type(self.get_object()), form=RelationForm, exclude=[])

    def get_success_url(self):
        return reverse("relationupdate", args=[self.get_object().id,])


class RelationDelete(DeleteView):
    template_name = "confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        res = super().delete(request, args, kwargs)
        if 'status_only' in self.request.GET:
            return HttpResponse()
        return res

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])

    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET.get("next")
        contenttype = ContentType.objects.get_for_model(self.get_object())
        return reverse("relation", args=[contenttype.id,])
