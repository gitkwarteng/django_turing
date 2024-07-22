import pandas as pd
from django.contrib import messages
from django.db import transaction
from django.views.generic import FormView

from .forms import ExcelUploadForm
from .models import Product


class UploadProductsView(FormView):
    """Upload products view."""

    template_name = 'excel/upload_excel.html'
    form_class = ExcelUploadForm
    success_url = '/excel/upload/'

    def get_context_data(self, **kwargs):
        """Get context data."""
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

    def form_valid(self, form):
        """Form valid callback."""
        file = form.cleaned_data['excel_file']
        try:
            self.process_import(file)

            messages.success(self.request,
                             'Products uploaded successfully!')

        except Exception as e:
            print(f'Error processing file: {e}')
            messages.error(self.request,
                           f'Error processing file: {e}')

        return super().form_valid(form)

    def process_import(self, file):
        """Process import."""
        df = pd.read_excel(file)

        # Sanitize column names
        df.columns = [col.strip().replace(' ', '_').lower()
                      for col in df.columns]

        # Get all fields from the Product model
        product_fields = [f.name for f in
                          Product._meta.get_fields()]

        # Use a transaction for efficiency and data integrity
        with transaction.atomic():
            for index, row in df.iterrows():
                data = dict(zip(df.columns, row.values))

                try:
                    # Filter out fields that don't exist in the model
                    data = {
                        field_name: value for field_name,
                        value in data.items()
                        if field_name in product_fields
                    }

                    # Variables to store ManyToMany data
                    many_to_many = {}

                    for field_name, value in data.items():
                        model_field = Product._meta.get_field(field_name)

                        # Handle Many-to-Many relationships
                        if model_field.many_to_many:
                            related_objects = []
                            for related_value in str(value).split(','):
                                related_obj, created = model_field. \
                                    related_model.objects.get_or_create(
                                        name=related_value.strip()
                                    )
                                related_objects.append(related_obj)
                            # Add related objects after the product is created
                            many_to_many[field_name] = related_objects
                        # Use is_relation to check for ForeignKey
                        elif model_field.is_relation:
                            # Handle foreign key relationships
                            related_obj, created = model_field. \
                                related_model.objects.get_or_create(
                                    name=value
                                )
                            data[field_name] = related_obj
                        else:
                            # Basic type conversion
                            if isinstance(value, str):
                                value = value.strip()
                            data[field_name] = value

                    # Remove related fields from data
                    for field_name in many_to_many.keys():
                        del data[field_name]

                    # Create Product object
                    product = Product.objects.create(**data)

                    # Now add the ManyToMany relationships
                    for field_name, related_objects in many_to_many.items():
                        getattr(product, field_name).set(related_objects)

                except Exception as e:
                    print(f"Error processing row {index + 1}: {e}")
                    messages.error(self.request,
                                   f"Error processing row {index + 1}: {e}")
                    continue
