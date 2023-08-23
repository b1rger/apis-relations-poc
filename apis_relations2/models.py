from apis_core.apis_metainfo.models import RootObject
from django.db import models
from django.db.models.base import ModelBase
from django.core.exceptions import ValidationError
from model_utils.managers import InheritanceManager


# This ModelBase is simply there to check if the needed attributes
# are set in the Relation child classes.
class RelationModelBase(ModelBase):
    def __new__(metacls, name, bases, attrs):
        if name == "Relation":
            return super().__new__(metacls, name, bases, attrs)
        else:
            new_class = super().__new__(metacls, name, bases, attrs)
            if not hasattr(new_class, 'subj_model'):
                raise ValueError("%s inherits from Relation and must therefore specify subj_model" % name)
            if not hasattr(new_class, 'obj_model'):
                raise ValueError("%s inherits from Relation and must therefore specify obj_model" % name)

            return new_class


class Relation(models.Model, metaclass=RelationModelBase):
    subj = models.ForeignKey(RootObject, on_delete=models.SET_NULL, null=True, related_name="relations_as_subj")
    obj = models.ForeignKey(RootObject, on_delete=models.SET_NULL, null=True, related_name="relations_as_obj")

    metadata = models.JSONField(null=True, editable=False)

    objects = InheritanceManager()

    def save(self, *args, **kwargs):
        if self.subj:
            subj = RootObject.objects_inheritance.get_subclass(id=self.subj.id)
            if not isinstance(subj, self.subj_model):
                raise ValidationError(f"{self.subj} is not of type {self.subj_model._meta.label}")
        if self.obj:
            obj = RootObject.objects_inheritance.get_subclass(id=self.obj.id)
            if not isinstance(obj, self.obj_model):
                raise ValidationError(f"{self.obj} is not of type {self.obj_model._meta.label}")
        super().save(*args, **kwargs)

    @property
    def subj_to_obj_text(self):
        if hasattr(self, "name"):
            return f"{self.subj} {self.name} {self.obj}"
        return f"{self.subj} relation to {self.obj}"

    @property
    def obj_to_subj_text(self):
        if hasattr(self, "reverse_name"):
            return f"{self.subj} {self.reverse_name} {self.obj}"
        return f"{self.obj} relation to {self.subj}"

    def __str__(self):
        return self.subj_to_obj_text
