# Generated by Django 3.1.5 on 2021-05-10 00:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gymnast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rtn_id', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=100)),
                ('year', models.CharField(choices=[('FR', 'Freshman'), ('SO', 'Sophomore'), ('JR', 'Junior'), ('SR', 'Senior')], max_length=2)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'team')},
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('roster_size', models.PositiveIntegerField()),
                ('lineup_size', models.PositiveIntegerField()),
                ('event_lineup_size', models.PositiveIntegerField()),
                ('event_count_size', models.PositiveIntegerField()),
                ('currently_drafting', models.PositiveIntegerField(blank=True, default=0)),
                ('draft_started', models.BooleanField(default=False)),
                ('draft_complete', models.BooleanField(default=False)),
                ('going_down', models.BooleanField(default=True)),
                ('drafted', models.ManyToManyField(blank=True, related_name='DraftedGymnasts', to='core.Gymnast')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='League', to=settings.AUTH_USER_MODEL)),
                ('requested_to_join', models.ManyToManyField(blank=True, related_name='RequestedLeague', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FantasyTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('wins', models.PositiveIntegerField(default=0)),
                ('losses', models.PositiveIntegerField(default=0)),
                ('draft_position', models.PositiveIntegerField(default=0)),
                ('currently_in_draft', models.BooleanField(default=False)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FantasyTeam', to='core.league')),
                ('roster', models.ManyToManyField(blank=True, related_name='FantasyTeam', to='core.Gymnast')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FantasyTeam', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'league')},
            },
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('sumbitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contactus', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('week', models.PositiveIntegerField()),
                ('meet', models.CharField(max_length=100)),
                ('event', models.CharField(choices=[('FX', 'Floor Exercise'), ('PH', 'Pommel Horse'), ('SR', 'Still Rings'), ('VT', 'Vault'), ('PB', 'Parallel Bars'), ('HB', 'Horizontal Bar')], max_length=2)),
                ('score', models.DecimalField(decimal_places=4, max_digits=6)),
                ('gymnast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Scores', to='core.gymnast')),
            ],
            options={
                'unique_together': {('gymnast', 'date', 'event')},
            },
        ),
        migrations.CreateModel(
            name='LineUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('FX', 'Floor Exercise'), ('PH', 'Pommel Horse'), ('SR', 'Still Rings'), ('VT', 'Vault'), ('PB', 'Parallel Bars'), ('HB', 'Horizontal Bar')], max_length=2)),
                ('week', models.PositiveIntegerField()),
                ('gymnasts', models.ManyToManyField(blank=True, related_name='LineUp', to='core.Gymnast')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='LineUp', to='core.fantasyteam')),
            ],
            options={
                'ordering': ['id'],
                'unique_together': {('team', 'event', 'week')},
            },
        ),
    ]
