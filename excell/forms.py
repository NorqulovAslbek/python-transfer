from django import forms


class ExcelImportForm(forms.Form):
    file = forms.FileField(label="Excel faylni tanlang")
