from django import forms


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Select Excel File', help_text='Only Excel files are allowed')
    # Add any additional fields or customizations as needed