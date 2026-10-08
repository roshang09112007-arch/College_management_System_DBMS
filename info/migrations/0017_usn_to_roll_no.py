from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0016_auto_20210820_1553'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='USN',
            new_name='roll_no',
        ),
        migrations.AlterField(
            model_name='student',
            name='roll_no',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='Roll No'),
        ),
    ]
