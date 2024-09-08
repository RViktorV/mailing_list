# Generated by Django 4.2.2 on 2024-09-07 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0003_alter_client_options_alter_mailing_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailing',
            options={'permissions': [('watch_mailings', 'Может просматривать любые рассылки'), ('deactivate_mailings', 'Может отключать рассылки')], 'verbose_name': 'Рассылка', 'verbose_name_plural': 'Рассылки'},
        ),
        migrations.AddField(
            model_name='mailing',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время окончания рассылки'),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='periodicity',
            field=models.CharField(choices=[('D', 'Ежедневно'), ('W', 'Еженедельно'), ('M', 'Ежемесячно')], max_length=1),
        ),
    ]
