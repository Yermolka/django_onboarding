# Generated by Django 5.0.2 on 2024-02-22 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_question_possible_answers_alter_question_constraint_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(max_length=100, verbose_name='Ответ'),
        ),
    ]
