from django.forms import ModelForm
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper


class RelationForm(ModelForm):
    def __init__(self, fromsubj=None, hxnext=None, reversed=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if fromsubj:
            if not reversed:
                self.fields["subj"].disabled = True
                self.fields["subj"].initial = get_object_or_404(self._meta.model.subj_model, id=fromsubj)
                self.fields["obj"].queryset = self._meta.model.obj_model.objects.all()
            else:
                self.fields["obj"].disabled = True
                self.fields["obj"].initial = get_object_or_404(self._meta.model.obj_model, id=fromsubj)
                self.fields["subj"].queryset = self._meta.model.subj_model.objects.all()

        self.helper = FormHelper(self)

        contenttype = ContentType.objects.get_for_model(self._meta.model).pk

        args = [contenttype,]
        if fromsubj:
            args.append(fromsubj)
        hx_post = reverse("relation", args=args)
        obj_contenttype = ContentType.objects.get_for_model(self._meta.model.obj_model)
        if reversed:
            hx_post = reverse("relationreversed", args=args)
            obj_contenttype = ContentType.objects.get_for_model(self._meta.model.subj_model)

        if hxnext:
            hx_post += f"?hx-next={hxnext}"

        self.helper.attrs = {
            "hx-post": hx_post,
            "hx-target": f"#{obj_contenttype.name}_table",
            "hx-swap": "outerHTML",
        }
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
