from django.forms import ModelForm, Textarea, modelformset_factory, RadioSelect, Select, IntegerField
from depreciation_rate_classifier.models import UserInput, UserConfirmation


class UserInputForm(ModelForm):
    class Meta:
        model = UserInput
        fields = ['user_input']
        widgets = {
            'user_input': Textarea(attrs={'cols': 80, 'rows': 15}),
        }


class UserConfirmationForm(ModelForm):
    class Meta:
        model = UserConfirmation
        fields = ['user_feedback']
        widgets = {'user_feedback': RadioSelect}
