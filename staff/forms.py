from django import forms
from django.db.models.functions import Lower


def user_label_from_instance(obj):
    full_name = obj.get_full_name()
    return f"{obj.email} ({full_name})" if full_name else obj.email


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return user_label_from_instance(obj)


class PickUsersMixin:
    """
    A generic form for picking Users to link to another object.

    We connect users to different objects (eg Orgs) via membership models.  In
    the Staff Area we want a UI to handle creating those connections.  In
    particular we want to order Users by their email, ignoring case, and
    display them with both email and full name.
    """

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = users.order_by(Lower("name"))
        self.fields["users"] = UserModelMultipleChoiceField(queryset=users)


class OrgAddMemberForm(PickUsersMixin, forms.Form):
    pass
