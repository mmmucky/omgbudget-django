from django import forms


class UploadTransactionsForm(forms.Form):
    file = forms.FileField()


class UploadClassificationsForm(forms.Form):
    file = forms.FileField()
