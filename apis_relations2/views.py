from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView, ProcessFormView, FormMixin, ProcessFormView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import Http404

from django_tables2 import SingleTableView, SingleTableMixin

from .models import Relation
from .forms import RelationForm
from .utils import relation_content_types
from .tables import RelationTable


class RelationsList(ListView):
    template_name = "relations_list.html"
    model = Relation

    def get_queryset(self):
        return super().get_queryset().select_subclasses()


class RelationMixin:
    def dispatch(self, request, *args, **kwargs):
        self.contenttype = ContentType.objects.get_for_id(kwargs.get("contenttype"))
        # TODO: use utils or check for None
        if self.contenttype not in relation_content_types():
            raise Http404(f"Relation with id {kwargs['contenttype']} does not exist")
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        exclude = []
        return modelform_factory(self.contenttype.model_class(), form=RelationForm, exclude=exclude)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["fromsubj"] = self.kwargs.get("fromsubj")
        kwargs["next"] = self.request.GET.get("next")
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['contenttype'] = self.contenttype
        return ctx


#TODO: rename this to Relation and make it work with and without subj (like the partial version of the view)
class RelationType(RelationMixin, ProcessFormView, FormMixin, ListView):
    template_name = "relations_list.html"

    # we have to explicitly call the ListView.get method, because the
    # ProcessFormView overrides it in https://github.com/django/django/blob/4f0c0e6fa1ce2e4da9407f122d0c1c27c7f8ad83/django/views/generic/edit.py#L140
    def get(self, request, *args, **kwargs):
        return super(ListView, self).get(request, args, kwargs)

    def get_queryset(self):
        return self.contenttype.model_class().objects.all()

    def get_success_url(self):
        args = [self.contenttype.id,]
        if self.kwargs.get("fromsubj"):
            args.append(self.kwargs.get("fromsubj"))
        return reverse("relationtypefrom", args=args) + "?success"

class RelationViewPartial(RelationMixin, SingleTableMixin, CreateView):
    template_name = "partial.html"
    table_class = RelationTable

    def get_success_url(self):
        return reverse("relationpartial", args=[self.contenttype.pk, self.kwargs.get("fromsubj")]) + "?success"

    def get_context_data(self):
        ctx = super().get_context_data()
        if "success" in self.request.GET:
            ctx['form'] = None
        else:
            ctx['table'] = None
        return ctx

    def get_queryset(self):
        if self.kwargs.get("fromsubj"):
            return self.contenttype.model_class().objects.filter(subj=self.kwargs.get("fromsubj"))
        return self.contenttype.model_class().objects.all()


class RelationUpdate(UpdateView):
    template_name = "relations_list.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])

    def get_form_class(self):
        exclude = []
        return modelform_factory(type(self.get_object()), form=RelationForm, exclude=exclude)

    def get_success_url(self):
        return reverse("relationupdate", args=[self.get_object().id,])


class RelationDelete(DeleteView):
    template_name = "confirm_delete.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])

    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET.get("next")
        contenttype = ContentType.objects.get_for_model(self.get_object())
        return reverse("relationtype", args=[contenttype.id,])
