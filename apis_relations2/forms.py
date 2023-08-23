from django.forms import ModelForm
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from crispy_forms.layout import Submit, Layout, Row, Column
from crispy_forms.helper import FormHelper


class RelationForm(ModelForm):
    def __init__(self, fromsubj=None, next=None, *args, **kwargs):
        if fromsubj:
            kwargs["initial"]["subj"] = get_object_or_404(self._meta.model.subj_model, id=fromsubj)

        super().__init__(*args, **kwargs)

        if fromsubj:
            self.fields["subj"].disabled = True
        else:
            self.fields["subj"].queryset = self._meta.model.subj_model.objects.all()
        self.fields["obj"].queryset = self._meta.model.obj_model.objects.all()

        self.helper = FormHelper(self)

        contenttype = ContentType.objects.get_for_model(self._meta.model).pk
        self.helper.form_action = reverse("relationtype", args=[contenttype])
        if fromsubj:
            self.helper.form_action = reverse("relationtypefrom", args=[contenttype, fromsubj])

        if next:
            self.helper.form_action += f"?next={next}"

        self.helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
