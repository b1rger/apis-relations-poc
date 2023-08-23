from django.db.models import ForeignKey


class RelationKey(ForeignKey):

    def contribute_to_class(self, cls, name):
        print(cls)
        if hasattr(cls, 'subj_model'):
            cls.subj.limit_choices_to = self.subj_model.objects.all()
