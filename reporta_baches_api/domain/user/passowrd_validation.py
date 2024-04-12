import re
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext as _
from django.utils import timezone

#from lib.ddd.global_value_objects import PasswordValidationErrorCodes

from .models import PreviousPassword

class ComplexityValidator:
    def __init__(self, **kwargs):
        self.min_char_categories = kwargs.pop('min_char_categories', 4)
        self.min_chars_of_each_type = [
            ('min_numeric_chars', r'[0-9]', 'Numbers', "Numbers are required"),
            ('min_uppercase_chars', r'[A-Z]', 'Uppercase letters',"You need a uppercase letter"),
            ('min_lowercase_chars', r'[a-z]', 'Lowercase letters', "You need a lowercase letter"),
            ('min_special_chars', r'[^0-9A-Za-z]', 'Special characters', "You need a special character"),
        ]
        for attr, _regex, _name, _ in self.min_chars_of_each_type:
            setattr(self, attr, kwargs.get(attr, 1))
    
    def validate(self, password, user=None):
        errors = []
        char_types_contained = 0
        for attr, regex, name, error_code in self.min_chars_of_each_type:
            find = re.findall(regex, password)
            required = getattr(self, attr)
            if len(find) < required:
                errors.append(
                    ValidationError(f"Password must include at least {required} characters of {name}",
                    error_code)
                )
            if find:
                char_types_contained += 1

        if char_types_contained < self.min_char_categories:
            errors.append(
                ValidationError(f"Password must contain at least {self.min_char_categories} of the following: uppercase letters, lowercase letters, numbers, special symbols",
                code="You need more complexity for your password")
            )

        if errors:
            raise ValidationError(errors)
        
    def get_help_text(self):
        requirements = []
        for attr, _, name, _ in self.min_chars_of_each_type:
            required = getattr(self, attr)
            if required:
                requirements.append(f"At least {required} characters of {name}")
        if self.min_char_categories:
            requirements.append(f"Password must contain at least {self.min_char_categories} of the following: uppercase letters, lowercase letters, numbers, special symbols")

        return f"Password must include {'; '.join(requirements)}."
    

    def __init__(self, min_interval_days=1):
        self.min_interval = timedelta(days=min_interval_days)

    def validate(self, password, user=None):
        if user is None:
            return None
        
        if user.last_password_change is None:
            return None
        
        if (timezone.now() - user.last_password_change) < self.min_interval:
            raise ValidationError(
                _("You must wait at least {} day(s) to change your password again.").format(self.min_interval.days),
                code=10,
            )

    def get_help_text(self):
        return _("You must wait at least {} day(s) to change your password again.").format(self.min_interval.days)