from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView, ProcessFormView, FormMixin, ProcessFormView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import Http404

from .models import Relation
from .forms import RelationForm
from .utils import relation_content_types


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


class RelationType(RelationMixin, FormMixin, ListView):
    template_name = "relations_list.html"

    def get_queryset(self):
        return self.contenttype.model_class().objects.all()

    def post(self, request, *args, **kwargs):
        view = RelationCreateViewPartial.as_view()
        return view(request, *args, **kwargs)


class RelationCreateViewPartial(RelationMixin, CreateView):
    template_name = "partial.html"

    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET.get("next")
        if self.kwargs.get("fromsubj"):
            return get_object_or_404(self.contenttype.model_class().subj_model, id=self.kwargs.get("fromsubj")).get_absolute_url()
        return reverse("relationtype", args=[self.contenttype.pk])


class RelationUpdate(UpdateView):
    template_name = "relations_list.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])

    def get_form_class(self):
        exclude = []
        return modelform_factory(type(self.get_object()), form=RelationForm, exclude=exclude)


class RelationDetail(DetailView):
    template_name = "relation_detail.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])


class RelationDelete(DeleteView):
    template_name = "confirm_delete.html"

    def get_object(self):
        return Relation.objects.get_subclass(id=self.kwargs["pk"])
