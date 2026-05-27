from django import forms
from .models import HollandQuestion

class HollandTestForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for q in questions:
            self.fields[f'question_{q.id}'] = forms.ChoiceField(
                label=q.text,
                choices=[(5, 'Полностью согласен'), (4, 'Согласен'), (3, 'Нейтрально'), (2, 'Не согласен'), (1, 'Полностью не согласен')],
                widget=forms.RadioSelect,
                required=True
            )