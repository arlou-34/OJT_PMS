# Generated by Django 5.2.1 on 2025-06-11 02:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('placement', '0012_alter_evaluation_student_delete_practicumevaluation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='placement.student'),
        ),
    ]
