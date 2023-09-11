from django.forms import ModelForm
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


from crispy_forms.layout import Submit, Layout, Div
from crispy_forms.helper import FormHelper


class RelationForm(ModelForm):
    def __init__(self, frominstance=None, tocontenttype=None, hxnext=None, inverted=False, embedded=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        subj, obj = "subj", "obj"
        if inverted:
            subj = "obj"
            obj = "subj"

        if frominstance:
            self.fields[subj].disabled = True
            self.fields[subj].initial = frominstance
            self.fields[subj].label = ContentType.objects.get_for_model(frominstance).name

        if tocontenttype:
            self.fields[obj].queryset = tocontenttype.model_class().objects.all()
            self.fields[obj].label = tocontenttype.name

        self.helper = FormHelper(self)

        relcontenttype = ContentType.objects.get_for_model(self._meta.model)

        args = [relcontenttype.pk,]
        if frominstance:
            args.append(ContentType.objects.get_for_model(frominstance).pk)
            args.append(frominstance.pk)
        if tocontenttype:
            args.append(tocontenttype.pk)
        hx_post = reverse("relation", args=args)
        if inverted:
            hx_post = reverse("relationinverted", args=args)
        hx_post += "?partial"

        if hxnext:
            hx_post += f"&hx-next={hxnext}"

        if embedded:
            self.helper.attrs = {
                "hx-post": hx_post,
                "hx-target": "closest #relation",
                "hx-swap": "outerHTML",
            }

        # layout stuff:
        div = Div(Div('subj', css_class='col-md-6'), Div('obj', css_class='col-md-6'), css_class='row')
        if inverted:
            div = Div(Div('obj', css_class='col-md-6'), Div('subj', css_class='col-md-6'), css_class='row')

        # we have to explicetly add the rest of the fields
        fields = {k: v for k, v in self.fields.items() if k not in ['obj', 'subj']}

        self.helper.layout = Layout(
                div,
                *fields,
        )
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))

    #def clean(self):
    #    subj = self.cleaned_data["subj"]
    #    if not type(subj) in self._meta.model.subj_list():
    #        raise ValidationError("Subj of wrong type")
