# Generated by Django 3.1.1 on 2020-09-26 03:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Colour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Colour code.', max_length=20, unique=True)),
                ('description', models.CharField(blank=True, help_text='Colour description.', max_length=64)),
                ('rgb_colour', models.CharField(blank=True, help_text='RGB colour.', max_length=8)),
                ('contrast_colour', models.CharField(blank=True, help_text='Contrasting colour.', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='PartType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Code.', max_length=20, unique=True)),
                ('description', models.CharField(help_text='Description.', max_length=64)),
                ('picture', models.ImageField(blank=True, help_text='Picture.', upload_to='myLego/static/parts/')),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Code.', max_length=20, unique=True)),
                ('description', models.CharField(help_text='Description.', max_length=64)),
                ('set_classes', models.CharField(blank=True, help_text='Class(es).', max_length=80)),
                ('year_released', models.IntegerField(blank=True, help_text='Year of release.', null=True)),
                ('num_pieces', models.IntegerField(default=0, help_text='Number of pieces.')),
                ('picture', models.ImageField(blank=True, help_text='Picture.', upload_to='myLego/static/sets/')),
                ('instructionURL', models.URLField(blank=True, help_text='URL to build instructions.')),
            ],
        ),
        migrations.CreateModel(
            name='SetPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_qty', models.IntegerField(default=0, help_text='Quantity.')),
                ('part_notes', models.CharField(blank=True, help_text='Notes.', max_length=64)),
                ('for_set', models.ForeignKey(blank=True, default=None, help_text='For set.', null=True, on_delete=django.db.models.deletion.CASCADE, to='myLego.set')),
                ('req_col', models.ForeignKey(default=None, help_text='Colour.', on_delete=django.db.models.deletion.CASCADE, to='myLego.colour')),
                ('req_part', models.ForeignKey(default=None, help_text='Part.', on_delete=django.db.models.deletion.CASCADE, to='myLego.parttype')),
            ],
        ),
        migrations.CreateModel(
            name='MyPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocation', models.ForeignKey(blank=True, default=None, help_text='Allocated to set.', null=True, on_delete=django.db.models.deletion.CASCADE, to='myLego.set')),
                ('colour', models.ForeignKey(help_text='Part colour.', on_delete=django.db.models.deletion.CASCADE, to='myLego.colour')),
                ('part', models.ForeignKey(help_text='Part type.', on_delete=django.db.models.deletion.CASCADE, to='myLego.parttype')),
            ],
        ),
    ]
