# Generated by Django 4.2.7 on 2024-02-21 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rustdesdevice",
            name="cpu",
            field=models.CharField(max_length=100, verbose_name="CPU"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="hostname",
            field=models.CharField(max_length=100, verbose_name="主机名"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="memory",
            field=models.CharField(max_length=100, verbose_name="内存"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="os",
            field=models.CharField(max_length=100, verbose_name="操作系统"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="username",
            field=models.CharField(blank=True, max_length=100, verbose_name="系统用户名"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="uuid",
            field=models.CharField(max_length=100, verbose_name="uuid"),
        ),
        migrations.AlterField(
            model_name="rustdesdevice",
            name="version",
            field=models.CharField(max_length=100, verbose_name="客户端版本"),
        ),
    ]
