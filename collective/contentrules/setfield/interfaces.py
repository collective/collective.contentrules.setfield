# -*- coding:utf-8 -*-
from collective.contentrules.setfield import SetFieldMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


items = [
    ("", u"Select"),
    ("object", u"Just the object"),
    ("all", u"All matching objects"),
]
terms = [
    SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in items
]


class ISetFieldAction(model.Schema):

    value_script = schema.Text(
        title=_(u"Value Script"),
        description=_(
            u"Enter PythonScript to calculate the values you want to"
            u" set. Return a dictionary of {'field': value}. "
            u"Available variables are: context, state, history, "
            u"event"
        ),
        default=_(u"""# values = {'field': some_value}"""),
        required=True,
    )

    update_all = schema.Choice(
        title=_("Update all content?"),
        description=_(
            u"Walks the site to update all matching content as well "
            u"as the item that triggered the content rule. May take"
            u"a long time to complete depending on how many objects"
            u"need to be updated."
        ),
        vocabulary=SimpleVocabulary(terms),
        default=u"object",
    )

    preserve_modification_date = schema.Bool(
        title=_("Preserve modification date?"),
        description=_(
            "Does not change the modification date. Beware that the action"
            " that triggered the rule may update the modification date and"
            " this setting will not override it"
        ),
    )

    model.fieldset(
        "script",
        label=_(u"Script"),
        fields=["value_script"],
    )

    model.fieldset(
        "advanced",
        label=_(u"Advanced"),
        fields=["update_all", "preserve_modification_date"],
    )


class IParentModifiedEvent(IObjectEvent):
    """An objects parent has been modified"""
