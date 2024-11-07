from rest_pandas import PandasSerializer
from rest_framework import serializers
from file.models import File


class MyDataframeSerializer(PandasSerializer):
    class Meta:
        # Specify the fields you want to include, or use '__all__' to include everything
        fields = ('column1', 'column2', 'column3')


class CreateFileCleansingSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        exclude = [
            'id',
        ]


PROCESS_CHOICES = (
    ('delete_missing_row', 'Delete Missing Row'),
    ('delete_duplicate_row', 'Delete Duplicate Row'),
    ('data_type_conversion', 'Data type conversion'),
    ('delete_row_outlier', 'Delete Row Outlier'),
    ('impute_by_mean','Impute By Mean'),
    ('impute_by_mode','Impute By Mode'),
    ('remove_missing_cell', 'Remove Missing Cell'),
)


class ProcessFileCleansingSerializer(serializers.ModelSerializer):

    process = serializers.MultipleChoiceField(choices=PROCESS_CHOICES)

    class Meta:
        model = File
        fields = ("process", "created_by", "filename")