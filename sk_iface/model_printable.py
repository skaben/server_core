"""
Convert django.db.models.Model instance and all related ForeignKey, ManyToManyField and @property function fields into dict.

Usage:

    class MyDjangoModel(... PrintableModel):
        to_dict_fields = (...)
        to_dict_exclude = (...)

        ...

    a_dict = [inst.to_dict(fields=..., exclude=...) for inst in MyDjangoModel.objects.all()]
"""
import typing

import django.core.exceptions
import django.db.models
import django.forms.models

#nosend_fields = {'descr', '_state', 'id', 'online', 'uid', 'override', 'lock_id'}

def get_decorators_dir(cls, exclude: typing.Optional[set]=None) -> set:
    """
    Ref: https://stackoverflow.com/questions/4930414/how-can-i-introspect-properties-and-model-fields-in-django
    :param exclude: set or None
    :param cls:
    :return: a set of decorators
    """
    default_exclude = {"pk", "objects", "id"}
#    default_exclude.update(nosend_fields)
    if not exclude:
        exclude = default_exclude
    else:
        exclude = exclude.union(default_exclude)

    return set([name for name in dir(cls) 
                if name not in exclude 
                and isinstance(getattr(cls, name), property)])


class PrintableModel(django.db.models.Model):

    class Meta:
        abstract = True

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self, fields: typing.Optional[typing.Set]=None, exclude: typing.Optional[typing.Set]=None):
        opts = self._meta
        data = {}

        # support fields filters and excludes
        if not fields:
            fields = set()
        else:
            fields = set(fields)
        default_fields = getattr(self, "to_dict_fields", set())
        fields = fields.union(default_fields)

        if not exclude:
            exclude = set()
        else:
            exclude = set(exclude)
        default_exclude = getattr(self, "to_dict_exclude", set())
        exclude = exclude.union(default_exclude)

        # support syntax "field__childField__..."
        self_fields = set()
        child_fields = dict()
        if fields:
            for i in fields:
                splits = i.split("__")
                if len(splits) == 1:
                    self_fields.add(splits[0])
                else:
                    field_name = splits[0]
                    if field_name not in child_fields:
                        child_fields[field_name] = set()
                    child_fields[field_name].add("__".join(splits[1:]))

        self_exclude = set()
        child_exclude = dict()
        if exclude:
            for i in exclude:
                splits = i.split("__")
                if len(splits) == 1:
                    self_exclude.add(splits[0])
                else:
                    field_name = splits[0]
                    if field_name not in child_exclude:
                        child_exclude[field_name] = set()
                    child_exclude[field_name].add("__".join(splits[1:]))

        for f in opts.concrete_fields + opts.many_to_many:
            if self_fields and f.name not in self_fields:
                continue
            if self_exclude and f.name in self_exclude:
                continue

            if isinstance(f, django.db.models.ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    result = []
                    m2m_inst = f.value_from_object(self)
                    for obj in m2m_inst:
                        if isinstance(obj, PrintableModel) and hasattr(obj, "to_dict"):
                            d = obj.to_dict(
                                fields=child_fields.get(f.name),
                                exclude=child_exclude.get(f.name),
                            )
                        else:
                            d = django.forms.models.model_to_dict(
                                obj,
                                fields=child_fields.get(f.name),
                                exclude=child_exclude.get(f.name)
                            )
                        result.append(d)
                    data[f.name] = result
            elif isinstance(f, django.db.models.ForeignKey):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = None
                    try:
                        foreign_inst = getattr(self, f.name)
                    except django.core.exceptions.ObjectDoesNotExist:
                        pass
                    else:
                        if isinstance(foreign_inst, PrintableModel) and hasattr(foreign_inst, "to_dict"):
                            data[f.name] = foreign_inst.to_dict(
                                fields=child_fields.get(f.name),
                                exclude=child_exclude.get(f.name)
                            )
                        elif foreign_inst is not None:
                            data[f.name] = django.forms.models.model_to_dict(
                                foreign_inst,
                                fields=child_fields.get(f.name),
                                exclude=child_exclude.get(f.name),
                            )

            elif isinstance(f, (django.db.models.DateTimeField, django.db.models.DateField)):
                v = f.value_from_object(self)
                if v is not None:
                    data[f.name] = v.isoformat()
                else:
                    data[f.name] = None
            else:
                data[f.name] = f.value_from_object(self)

        # support @property decorator functions
        decorator_names = get_decorators_dir(self.__class__)
        for name in decorator_names:
            if self_fields and name not in self_fields:
                continue
            if self_exclude and name in self_exclude:
                continue

            value = getattr(self, name)
            if isinstance(value, PrintableModel) and hasattr(value, "to_dict"):
                data[name] = value.to_dict(
                    fields=child_fields.get(name),
                    exclude=child_exclude.get(name)
                )
            elif hasattr(value, "_meta"):
                # make sure it is a instance of django.db.models.fields.Field
                data[name] = django.forms.models.model_to_dict(
                    value,
                    fields=child_fields.get(name),
                    exclude=child_exclude.get(name),
                )
            elif isinstance(value, (set, )):
                data[name] = list(value)
            else:
                data[name] = value

        return data


