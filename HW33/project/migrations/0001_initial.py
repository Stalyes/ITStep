import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='სახელი')),
                ('last_name', models.CharField(max_length=50, verbose_name='გვარი')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='ელ-ფოსტა')),
                ('biography', models.TextField(blank=True, verbose_name='ბიოგრაფია')),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='წიგნის დასახელება')),
                ('summary', models.TextField(blank=True, verbose_name='მოკლე აღწერა')),
                ('pages', models.PositiveIntegerField(default=1, verbose_name='გვერდები')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='books', to='project.author', verbose_name='ავტორი')),
            ],
        ),
        migrations.CreateModel(
            name='Reader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='სახელი')),
                ('last_name', models.CharField(max_length=50, verbose_name='გვარი')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='ელ-ფოსტა')),
                ('joined_at', models.DateField(auto_now_add=True, verbose_name='გაწევრიანების თარიღი')),
                ('books', models.ManyToManyField(blank=True, related_name='readers', to='project.book', verbose_name='წიგნები')),
            ],
        ),
    ]
