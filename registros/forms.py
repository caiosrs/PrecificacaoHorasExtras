#registros/forms.py

from django import forms
from .models import RegistroHorasExtras
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RegistroHorasExtrasForm(forms.ModelForm):
    class Meta:
        model = RegistroHorasExtras
        fields = ['nome_funcionario', 'dias_uteis', 'dsr', 'he60_qtde', 'he80_qtde', 'he80_qtde_noturno', 'he100_qtde']

    dias_uteis = forms.IntegerField(label='Dias Úteis')
    dsr = forms.FloatField(label='DSR')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Salvar', css_class='btn-primary'))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

    def clean(self):
        cleaned_data = super().clean()
        fields_to_default = ['he60_qtde', 'he80_qtde', 'he80_qtde_noturno', 'he100_qtde']
        
        for field in fields_to_default:
            value = cleaned_data.get(field)
            if value:
                # Substituir vírgulas por pontos
                value = value.replace(',', '.')
                try:
                    # Tentar converter para float
                    cleaned_data[field] = float(value)
                except ValueError:
                    self.add_error(field, "Por favor, insira um valor numérico válido.")
            else:
                cleaned_data[field] = 0.0  # Definir padrão como 0.0
                
        return cleaned_data