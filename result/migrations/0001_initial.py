# Generated by Django 3.0.6 on 2020-06-07 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('student', '0002_carryoverstudent_repeatingstudent'),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakenCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ca', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('exam', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('total', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('grade', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')], max_length=1)),
                ('comment', models.CharField(blank=True, choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taken_courses', to='course.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gpa', models.FloatField(null=True)),
                ('cgpa', models.FloatField(null=True)),
                ('semester', models.CharField(choices=[('First', 'First'), ('Second', 'Second')], max_length=100)),
                ('session', models.CharField(blank=True, max_length=100, null=True)),
                ('level', models.CharField(choices=[('100', 100), ('200', 200), ('300', 300), ('400', 400), ('500', 500)], max_length=100)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.Student')),
            ],
        ),
    ]
