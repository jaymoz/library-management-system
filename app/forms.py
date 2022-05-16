from django import forms
from .models import *
from django.forms import CheckboxSelectMultiple, ModelForm
import django_filters
from django_filters import FilterSet
from django_filters import DateFilter
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

choices = Category.objects.all().values_list('name','name')

choice_list = [item for item in choices]

class BookForm(ModelForm):
	#for selecting multiple items
	category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=True, widget=CheckboxSelectMultiple)
	class Meta:
		model = Book
		fields = "__all__"
		widgets = {
			'name':forms.TextInput(attrs={
				'class':'input-text input-text--primary-style',
				'type':'text',
				'id':'address-fname',
				'required':True,
				'placeholder':'Title'
			}),
			'author':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-lname',
			'type':'text',
			'required':True,
			'placeholder':'Author'
			}),
			'isbn':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-street',
			'type':'text',
			'required':True,
			'placeholder':'isbn number'
			}),
			#for selecting only one item
			# 'category':forms.Select(choices=choice_list,attrs={
			# 'class':'input-text input-text--primary-style',
			# 'id':'address-phone',
			# 'type':'text',
			# 'required':True,
			# }),

			'description':forms.Textarea(attrs={
			'class':'text-area text-area--primary-style',
			'id':'address-phone',
			'type':'tel',
			'required':True,
			'placeholder':'Description',
			'cols':70,
			'rows':10,
			}),
			'quantity':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-phone',
			'type':'text',
			'required':True,
			'placeholder':'Quantity available'
			}),
			'slug':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-phone',
			'type':'text',
			'required':True,
			'placeholder':'slug field(book title in lower case)'
			}),
		}

class OrderFilterForm(django_filters.FilterSet):
	class Meta:
		model = Book
		fields = ["name","author","isbn","category"]
		widgets = {
			'category':django_filters.ModelMultipleChoiceFilter(attrs={
				'class':'form-control',
			})
		}		

class OrderForm(forms.ModelForm):
	class Meta:
		model = IssuedBooks
		fields = '__all__'

choice_list = ['Processing','Cancelled','Accepted','Returned']

class SetOrderStatusForm(forms.ModelForm):
	class Meta:
		model = IssuedBooks
		fields = ["status"]
		widgets = {
			'status':forms.Select(choices=choice_list,attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-phone',
			'type':'text',
			'required':True,
			}),
		}

class RegisterUserForm(UserCreationForm):
	username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'Username'
		}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'E-mail'
		}))
	first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'First Name'
		}))
	last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'Last Name'
		}))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'Password'
		}))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={
		'class':'form-control',
		'required':True,
		'placeholder':'Confirm Password'
		}))

	class Meta:
		model = User
		fields = ("username","first_name","last_name","email","password1","password2")

# class RegisterUserForm(forms.ModelForm):
# 	class Meta:
# 		model = User
# 		fields = '__all__'
# 		widgets = {
# 			'username':forms.TextInput(attrs={
# 				'class':'form-control',
# 				'type':'text',
# 				'id':'email',
# 				'required':True,
# 				'placeholder':'Username'
# 			}),
# 			'first_name':forms.TextInput(attrs={
# 				'class':'form-control',
# 				'type':'text',
# 				'id':'email',
# 				'required':True,
# 				'placeholder':'First Name'
# 			}),
# 			'last_name':forms.TextInput(attrs={
# 				'class':'form-control',
# 				'type':'text',
# 				'id':'email',
# 				'required':True,
# 				'placeholder':'Last Name'
# 			}),
# 			'email':forms.EmailInput(attrs={
# 				'class':'form-control',
# 				'type':'email',
# 				'id':'email',
# 				'required':True,
# 				'placeholder':'Email'
# 			}),
# 			'password':forms.PasswordInput(attrs={
# 				'class':'form-control',
# 				'type':'password',
# 				'id':'email',
# 				'required':True,
# 				'placeholder':'password'
# 			}),
# 		}


class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ["passport_no","nationality","phone","image"]
		widgets = {
			'passport_no':forms.TextInput(attrs={
				'class':'input-text input-text--primary-style',
				'type':'text',
				'id':'address-fname',
				'required':True,
				'placeholder':'Passport Number'
			}),
			'nationality':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-lname',
			'type':'text',
			'required':True,
			'placeholder':'Nationality'
			}),
			'phone':forms.TextInput(attrs={
			'class':'input-text input-text--primary-style',
			'id':'address-street',
			'type':'text',
			'required':True,
			'placeholder':'Phone Number'
			}),
		}
