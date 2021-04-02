# Generated by Django 3.0 on 2020-10-26 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Face',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('face_id', models.CharField(max_length=50, verbose_name='人脸ID')),
                ('name', models.CharField(max_length=30, verbose_name='姓名')),
                ('face_image', models.ImageField(upload_to='faces/%Y/%m/%d', verbose_name='人脸照片')),
                ('add_time', models.DateTimeField(auto_now=True, verbose_name='最后修改时间')),
            ],
            options={
                'verbose_name': '人脸上传',
                'verbose_name_plural': '人脸上传',
            },
        ),
        migrations.CreateModel(
            name='FaceGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('face_group_id', models.CharField(max_length=50, verbose_name='人脸组ID')),
                ('name', models.CharField(max_length=30, verbose_name='分组名')),
                ('description', models.CharField(default='', max_length=300, verbose_name='分组描述')),
                ('bound', models.BooleanField(default=False, verbose_name='是否被使用')),
                ('add_time', models.DateTimeField(auto_now=True, verbose_name='最后修改时间')),
            ],
            options={
                'verbose_name': '人脸库分组',
                'verbose_name_plural': '人脸库分组',
            },
        ),
    ]
