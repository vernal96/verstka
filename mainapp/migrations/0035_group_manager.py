# Generated by Django 3.2.7 on 2021-09-11 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0034_profile_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='manager',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, to='mainapp.educationalmanager', verbose_name='Менеджер учебного процесса'),
            preserve_default=False,
        ),
    ]
