# apis_relations2

This is a POC to demonstrate a new relation approach for APIS. Using this
django app you get a new model named `Relation`. In your `models.py` you can
inherit from this model to create new Relations. The models inheriting from
`Relation` have to set a `subj_model` and a `obj_model` - both pointing to
Django models. This limits the relation to those two types.

There is also a migration path from `TempTriple`: a `post_save` signal for
`TempTriple` `get_or_create`s a `Relation` with the same types and the same
`name` and `name_reverse` as the `TempTriple`. It then copies the field data
from the TempTriple to the Relation. This also works on updates of the
TempTriples.

Example:
```
class PersonHasLivingPlace(Relation, LegacyDateMixin):
    subj_model = Person
    obj_model = Place
    temptriple_name = "bewohnt"
    temptriple_name_reverse = "Bewohner von"
    temptriple_field_list = ['start_date', 'start_start_date', 'start_end_date', 'end_date', 'end_start_date', 'end_end_date', 'start_date_written', 'end_date_written']
```

(this example uses a `LegacyDateMixin` that defines the same datefields as `TempTriple`)
