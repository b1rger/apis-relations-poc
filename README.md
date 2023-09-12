# apis_relations2

This is a POC to demonstrate a new relation approach for APIS. Using this
django app you get a new model named `Relation`. In your `models.py` you can
inherit from this model to create new Relations. The models inheriting from
`Relation` have to set a `subj_model` and a `obj_model` - both pointing to
individual Django models or lists of Django models.
This setting limits the relation to those two types both in the save method and
in the form validation.

# Installation

Install as any other Django application. Create your relations. A very simple
Relation could look like this:

```Python
class PersonHasLivingPlace(Relation):
    subj_model = Person
    obj_model = Place
    name = "bewohnt"
    name_reverse = "Bewohner von"
```

The app uses `htmx` - but it should also work without it. Please test with and
without.

## Templatetags

There are a couple of templatetags to make the live with Relations easier:

`relations_table` gives you a list of relations. You can use the argument
`instance` to limit to relations a specific instance is part of. You can use
the argument `tocontenttype` to limit the list to relations that a have a
specific contenttype as object.

`instance_is_related_to instance` returns a list of Contenttypes this instance
*is* related to.

`relations_links` creates a list of links to relations views. The relations view
lists relations and provides a form to create new ones. You can use the argument
`instance` to limit to relations a specific instance is part of. You can use the
argument `tocontenttype` to limit to relations that have a specific contenttype
as object.

`instance_can_be_related_to` lists the contenttypes of all models an instance can
be related to. You have to pass the `instance` as an argument.

### Usage

In the existing APIS templates, you can use this block to override the relations
in `detail_generic.html`:
```
{% block relations %}
{% instance_is_related_to instance=object as contenttypes %}
{% for contenttype in contenttypes %}
<div class="card card-default">
  <div class="card-header" role="tab" id="heading{{ forloop.counter }}">
    <h4 class="card-title">
      <a role="button">{{ contenttype.name }}</a>
    </h4>
  </div>
    <div role="tabcard">
       <div class="card-body">
        {% relations_table instance=object tocontenttype=contenttype as table %}
	{% render_table table %}
    </div>
    </div>
  </div>
{% endfor %}
{% endblock %}
```

In the existing APIS templates, you can use this block to override the relations
in `edit_generic.html`:
```
{% instance_can_be_related_to instance as contenttypes %}
{% for contenttype in contenttypes %}
  <div class="card card-default">
    <div class="card-header" role="tab" id="heading{{ forloop.counter }}">
      <h4 class="card-title">
        <a role="button"
           data-toggle="collapse"
           data-parent="#accordion"
           href="#collapse{{ forloop.counter }}"
           aria-expanded="true"
           aria-controls="collapse{{ forloop.counter }}">{{ contenttype.name }}</a>
      </h4>
    </div>
    <div id="collapse{{ forloop.counter }}" class="card-collapse collapse" role="tabcard" aria-labelledby="heading{{ forloop.counter }}">
      <div id="tab_{{ obj.2 }}" class="card-body">
      {% relations_table instance=instance tocontenttype=contenttype as table %}
      {% render_table table %}

      {% relations_links instance=instance tocontenttype=contenttype htmx=True %}
    </div>
  </div>
{% endfor %}
```

# Migration from TempTripe

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
    name = "bewohnt"
    name_reverse = "Bewohner von"

    # Those are only for the Migration from TempTriple to Relation
    temptriple_name = "bewohnt"
    temptriple_name_reverse = "Bewohner von"
    temptriple_field_list = ['start_date', 'start_start_date', 'start_end_date', 'end_date', 'end_start_date', 'end_end_date', 'start_date_written', 'end_date_written']
```
