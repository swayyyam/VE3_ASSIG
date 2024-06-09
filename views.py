
import matplotlib
matplotlib.use('Agg')
import logging
logger = logging.getLogger(__name__)
from django.views.generic import DetailView, CreateView
from django.shortcuts import redirect
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from django.utils import timezone
from .forms import CSVFileForm
from .models import CSVFile
from django.urls import reverse, reverse_lazy
from django.contrib import messages


from django.contrib import messages

class UploadCSVView(CreateView):
    """
    UploadCSVView handles the uploading of CSV files, saving them to the database, and redirecting to the analysis page.
    """
    model = CSVFile
    form_class = CSVFileForm
    template_name = 'public_site/index.html'
    success_url = reverse_lazy('analysis:upload_csv')

    def form_valid(self, form):
        uploaded_file = self.request.FILES.get('file')
        if not uploaded_file.name.endswith('.csv'):
            messages.error(self.request, 'Please upload a CSV file.')
            return redirect('analysis:upload_csv')

        csv_file = form.save()
        return redirect(reverse('analysis:analyze_csv', kwargs={'pk': csv_file.id}))


class AnalyzeCSVView(DetailView):
    """
    AnalyzeCSVView analyzes the uploaded CSV file, performs data analysis, and schedules its deletion after 10 minutes.
    """
    model = CSVFile
    template_name = 'public_site/analyze.html'
    context_object_name = 'csv_file'

    def get_context_data(self, **kwargs):
        """
        Get additional context data for analysis and schedule deletion after 10 minutes.
        """
        context = super().get_context_data(**kwargs)
        csv_file = self.object
        if not os.path.exists(csv_file.file.path):
            return redirect('analysis:upload_csv')

        try:
            data = pd.read_csv(csv_file.file.path)

            # Data Analysis
            context['first_rows'] = self.style_table(data.head().to_html(classes='styled-table'))
            context['summary_stats'] = self.style_table(data.describe().to_html(classes='styled-table'))

            # Handle missing values
            context['missing_values'] = self.style_table(data.isnull().sum().to_frame(name='Missing Values').to_html(classes='styled-table'))

                    
            # Assuming 'data' is your DataFrame
            data_numeric = data.apply(pd.to_numeric, errors='coerce')
            data_numeric.dropna(inplace=True)

            # Additional statistics
            context['mean_values'] = self.style_table(data_numeric.mean().to_frame(name='Mean').to_html(classes='styled-table'))
            context['median_values'] = self.style_table(data_numeric.median().to_frame(name='Median').to_html(classes='styled-table'))
            context['std_dev_values'] = self.style_table(data_numeric.std().to_frame(name='Standard Deviation').to_html(classes='styled-table'))
            
            # Data Visualization
            histograms = {}
            for column in data.select_dtypes(include=[np.number]).columns:
                try:
                    plt.figure()
                    sns.histplot(data[column], kde=True)
                    img_path = os.path.join(settings.MEDIA_ROOT, f'histogram_{column}.png')
                    plt.savefig(img_path)
                    plt.close()  # Close the plot to avoid memory issues
                    histograms[column] = f'{settings.MEDIA_URL}histogram_{column}.png'
                except Exception as e:
                    logger.error(f"Error generating histogram for column {column}: {e}")
                    continue

            context['histograms'] = histograms

            # Schedule deletion after 10 minutes
            deletion_time = timezone.now() + timezone.timedelta(minutes=10)
            csv_file.delete_at = deletion_time
            csv_file.save()

            return context
        except FileNotFoundError:
            return redirect('analysis:upload_csv')
        
    def style_table(self, table_html):
        """
        Style HTML tables with CSS.
        """
        style = """
        <style>
            .styled-table {
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 0.9em;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-width: 300px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }
            .styled-table thead tr {
                background-color: #49a120;
                color: #ffffff;
                text-align: left;
            }
            .styled-table th,
            .styled-table td {
                padding: 12px 15px;
            }
            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .styled-table tbody tr:last-of-type {
                border-bottom: 2px solid #49a120;
            }
        </style>
        """
        return style + table_html
