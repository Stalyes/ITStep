from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="სახელი")
    last_name = models.CharField(max_length=50, verbose_name="გვარი")
    email = models.EmailField(unique=True, verbose_name="ელ-ფოსტა")
    biography = models.TextField(blank=True, verbose_name="ბიოგრაფია")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name="წიგნის დასახელება")
    summary = models.TextField(blank=True, verbose_name="მოკლე აღწერა")
    pages = models.PositiveIntegerField(default=1, verbose_name="გვერდები")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="ავტორი"
    )

    def __str__(self):
        return self.title


class Reader(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="სახელი")
    last_name = models.CharField(max_length=50, verbose_name="გვარი")
    email = models.EmailField(unique=True, verbose_name="ელ-ფოსტა")
    joined_at = models.DateField(auto_now_add=True, verbose_name="გაწევრიანების თარიღი")
    books = models.ManyToManyField(
        Book,
        related_name="readers",
        blank=True,
        verbose_name="წიგნები"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"