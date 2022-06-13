from unicodedata import lookup
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta
from django.shortcuts import reverse
from multiselectfield import MultiSelectField
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()
class Category(models.Model):
	name = models.CharField(max_length=100)

	class Meta:
		verbose_name_plural = 'Categories'
	
	def __str__(self):
		return self.name

class Book(models.Model):
	CHOICES = (
		('art & music', 'Arts & Music'),('biography','Biography'),('business','Business'),
		('comics','Comics'),('computer & tech','Computers & Tech'),('cooking','Cooking'),
		('edu & reference','Edu & Reference'),('entertainment','Entertainment'),('health & fitness','Health & Fitness'),
		('history','History'),('hobbies & crafts', 'Hobbies & Crafts'),('home & garden','Home & Garden'),
		('horror','Horror'),('kids','Kids'),('literature and fiction','Literature & Fiction'),('medical', 'Medical'),
		('mysteries','Mysteries'),('parenting','Parenting'),('religion','Religion'),('romance','Romance'),
		('sci-fi & fantasy', 'Sci-Fi & Fantasy'),('science & math', 'Science & Math'), ('self-help','Self-Help'),
		('social sciences','Social Sciences'),('sports','Sports'),('teen','Teen'),('travel','Travel'),
		('true crime', 'True Crime'),('western', 'Western'),
	)
	name = models.CharField(max_length=200)
	author = models.CharField(max_length=200)
	isbn = models.CharField(max_length=20, unique=True)
	book_cover_img = models.ImageField(upload_to="BookCoverImage", default="book_cover.png", null=True)
	category = models.ManyToManyField(Category)
	description = models.CharField(max_length=500)
	quantity = models.IntegerField(default=0)
	slug = models.SlugField()

	@property
	def imageURL(self):
		try:
			book_cover_img = self.book_cover_img.url
		except:
			book_cover_img = ''
		return book_cover_img

	def get_absolute_url(self):
		return reverse('home',kwargs={
		'slug':self.slug
		})

	def get_add_to_cart_url(self):
			return reverse('add',kwargs={
			'slug':self.slug
			})

	def get_remove_from_cart_url(self):
		return reverse('remove',kwargs={
			'slug':self.slug
			})
	def __str__(self):
		return str(self.name) + " ["+str(self.isbn)+']'

class OrderItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	book = models.ForeignKey(Book, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.quantity}x  {self.book.name}"

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	passport_no = models.CharField(max_length=20)
	nationality = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	image = models.ImageField( upload_to="UserProfile", default="default_user.png")

	@property
	def imageURL(self):
		try:
			image = self.image.url
		except:
			image = ''
		return image
	def __str(self):
		return self.user.id
	# def __str__(self):
	# 	return str(self.passport_no) + " " + str(self.user.first_name) + " " + str(self.user.last_name)


def expiry():
	return datetime.today() + timedelta(days=14)

class IssuedBooks(models.Model):
	STATUS_CHOICES  =(
		('processing','Processing'),
		('cancelled', 'Cancelled'),
		('accepted', 'Accepted'),
		('returned', 'Returned'),
		('expired', 'Expired')
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	status = models.CharField(max_length=100, choices=STATUS_CHOICES)
	ordered = models.BooleanField(default=False)
	books = models.ManyToManyField(OrderItem)
	issued = models.BooleanField(default=False)
	ordered_date = models.DateTimeField(blank=True,null=True)
	issued_date = models.DateTimeField(blank=True, null=True)
	expiry_date = models.DateTimeField(blank=True, null=True)


	class Meta:
		verbose_name_plural = "IssuedBooks"
	
	def __str__(self):
		return (self.status)

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)