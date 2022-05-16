from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import *
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def check_if_order_has_expired():
	all_orders = IssuedBooks.objects.filter(expiry_date__lte=datetime.now(timezone.utc))
	if all_orders.exists():
		for order in all_orders:
			order.status = "expired"
			order.save()


@login_required(login_url="/login")
def home(request):
	check_if_order_has_expired()
	books = Book.objects.all()
	user_profile = UserProfile.objects.filter(user=request.user)
	if not user_profile.exists():
		messages.info(request, "Create a User Profile for this account to be able to borrow books")
	myFilter = OrderFilterForm(request.GET, queryset=books)
	books = myFilter.qs
	context = {'items':books, 'myFilter':myFilter, 'user_profile':user_profile}
	return render(request, "app/home.html", context)

@login_required(login_url="/login")
def all_books(request):
	check_if_order_has_expired()
	books = Book.objects.all()
	user_profile = UserProfile.objects.filter(user=request.user)
	if not user_profile.exists():
		messages.info(request, "Create a User Profile for this account to be able to borrow books")
	myFilter = OrderFilterForm(request.GET, queryset=books)
	books = myFilter.qs
	context = {'items':books,'myFilter':myFilter}
	return render(request, "app/all-books.html", context)

@login_required(login_url="/login")
def add_to_cart(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		book=book,
		user=request.user,
		ordered=False
	)
	order_qs = IssuedBooks.objects.filter(user=request.user, ordered=False)
	if book.quantity > 0:
		if order_qs.exists():
			order = order_qs[0]
			if order.books.filter(book__slug=book.slug).exists():
				order_item.quantity += 1
				book.quantity -= 1
				book.save()
				order_item.save()
				messages.info(request, "This book quantity was updated")
				return redirect("home")
			else:
				order.books.add(order_item)
				book.quantity -= 1
				book.save()
				messages.info(request, "This book quantity was updated")
				return redirect("home")
		else:
			ordered_date = timezone.now()
			order = IssuedBooks.objects.create(user=request.user, ordered_date=ordered_date)
			order.books.add(order_item)
			messages.info(request, "This book was added to cart")
	else:
		messages.info(request, "This book is currently out of stock")
	return redirect("home")

@login_required(login_url="/login")
def remove_from_cart(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_qs = IssuedBooks.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.books.filter(book__slug=book.slug).exists():
			order_item = OrderItem.objects.filter(book=book,user=request.user,ordered=False)[0]
			i = 0
			while i < order_item.quantity:
				book.quantity += 1
				book.save()
				i += 1
			order.books.remove(order_item)
			order_item.delete()
			messages.info(request, "This book was removed from your cart")
			return redirect("home")
		else:
			messages.info(request, "This book was not in your cart")
			return redirect("home")
	else:
		messages.info(request,"You do not have an active order")
		return redirect("home")

@login_required(login_url="/login")
def remove_single_item_from_cart(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_qs = IssuedBooks.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(book__slug=book.slug).exists():
			order_item = OrderItem.objects.filter(
				book=book,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				book.quantity += 1
				book.save()
				order_item.save()
			else:
				order.books.remove(order_item)
			messages.info(request, "This book quantity was updated.")
			return redirect("home")
		else:
			messages.info(request, "This book was not in your cart")
			return redirect("home")
	else:
		messages.info(request, "You do not have an active Order")
		return redirect("home")

@login_required(login_url="/login")
def cart(request):
	check_if_order_has_expired()
	try:
		curr_order = IssuedBooks.objects.get(user=request.user, ordered=False)
		is_empty = curr_order.books.all().count()
		print(is_empty)
		context = {'order':curr_order,'is_empty':is_empty}
		if request.method == 'POST':
			order = IssuedBooks.objects.get(user=request.user, ordered=False)
			order_items = order.books.all()
			order_items.update(ordered=True)
			for item in order_items:
				item.save()
			order.ordered = True
			order.status = "processing"
			order.ordered_date = timezone.now()
			order.save()
			messages.success(request, "Your Issued_books was successfully created")
			return redirect("dashboard")
		return render(request, 'app/cart.html', context)
	except Exception as e:
		print(e, type(e))
		messages.info(request, "You do not have an active Issued_books")
		return redirect("home")

@login_required(login_url="/login")
def add_to_cart_page(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			book=book,
			user=request.user,
			ordered=False)
	order_qs = IssuedBooks.objects.filter(user=request.user, ordered=False)
	if book.quantity > 0:
		if order_qs.exists():
			order = order_qs[0]
			if order.books.filter(book__slug=book.slug).exists():
				order_item.quantity += 1
				book.quantity -= 1
				book.save()
				order_item.save()
				messages.info(request,"This book quantity was updated")
				return redirect("cart")
			else:
				order.books.add(order_item)
				book.quantity -= 1
				book.save()
				messages.info(request,"This book was added to cart")
				return redirect('cart')
		else:
			ordered_date = timezone.now()
			order = IssuedBooks.objects.create(user=request.user, ordered_date=ordered_date)
			order.books.add(order_item)
			messages.info(request,"This book quantity was updated")
	else:
		messages.info(request, "This book is currently out of stock")
	return redirect('cart')

@login_required(login_url="/login")
def remove_from_cart_page(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_qs = IssuedBooks.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order book is in the order
		if order.books.filter(book__slug=book.slug).exists():
			order_item = OrderItem.objects.filter(
				book=book,
				user=request.user,
				ordered=False
			)[0]
			i = 0
			while i < order_item.quantity:
				book.quantity += 1
				book.save()
				i += 1
			order.books.remove(order_item)
			order_item.delete()
			messages.info(request, "This book was removed from your cart.")
			return redirect("cart")
		else:
			messages.info(request, "This book was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")

@login_required(login_url="/login")
def remove_single_item_from_cart_page(request, slug):
	check_if_order_has_expired()
	book = get_object_or_404(Book, slug=slug)
	order_qs = IssuedBooks.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.books.filter(book__slug=book.slug).exists():
			order_item = OrderItem.objects.filter(
				book=book,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				book.quantity += 1
				book.save()
				order_item.quantity -= 1
				order_item.save()
			else:
				order.books.remove(order_item)
				book.quantity += 1
				book.save()
			messages.info(request, "This book quantity was updated.")
			return redirect("cart")
		else:
			messages.info(request, "This book was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")

@login_required(login_url="/login")
def order_detail(request, pk):
	check_if_order_has_expired()
	form = SetOrderStatusForm()
	single_order = get_object_or_404(IssuedBooks, id=pk, ordered=True)
	customer = User.objects.get(id = request.user.id)
	orders  = IssuedBooks.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = IssuedBooks.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'processing':processing, 'cancelled':cancelled, 'accepted':accepted,
	'recent_orders':recent_orders, 'single_order':single_order,'form':form
	}
	if request.method == 'POST':
		form = SetOrderStatusForm(request.POST)
		if form.is_valid():
			order_stat = form.cleaned_data.get('status')
			if order_stat == "processing":
				single_order.status = "processing"
				single_order.save()
				messages.success(request, "Order is currently being processed")
				return redirect("order-detail", pk=pk)

			if order_stat == "accepted":
				single_order.status = "accepted"
				single_order.issued = True
				single_order.expiry_date  = datetime.now() + timedelta(days=14)
				single_order.save()
				messages.success(request, "Order was successfully accepted")
				return redirect("order-detail", pk=pk)

			if order_stat == "cancelled":
				single_order.status = "cancelled"
				single_order.expiry_date  = None
				single_order.save()
				messages.success(request, "Order was successfully cancelled")
				return redirect("order-detail", pk=pk)

			if order_stat == "returned":
				single_order.status = "cancelled"
				single_order.expiry_date  = None
				single_order.save()
				messages.success(request, "Order was successfully cancelled")
				return redirect("order-detail", pk=pk)
				
	if single_order.expiry_date:
		days_left = single_order.expiry_date - datetime.now(timezone.utc)
		days_left = days_left.days
		context.update({'days_left':days_left})

	return render(request, 'app/order-detail.html', context)

@login_required(login_url="/login")
def dashboard(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	recent_orders  = IssuedBooks.objects.filter(user=request.user, ordered=True, issued=True).order_by('-ordered_date')[0:5]
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	context = {
		'orders':orders,'recent_orders':recent_orders,'processing':processing,
		'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders,
	}
	try:
		user_profile = get_object_or_404(UserProfile, user=request.user)
		context.update({'user_profile':user_profile})
	except:
		messages.info(request, "Kindly create a user profile for this account")
	return render(request, 'app/dashboard.html', context)

@login_required(login_url="/login")
def delete_book(request, pk):
	check_if_order_has_expired()
	book = get_object_or_404(Book, id=pk)
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == "POST":
		book.delete()
		messages.success(request, "This book was successfully deleted")
		return redirect("allBooks")

	context = {'book':book,'processing':processing,'accepted':accepted,'cancelled':cancelled,'total_orders':total_orders}
	return render(request, "app/delete-book.html", context)

@login_required(login_url="/login")
def add_book(request):
	check_if_order_has_expired()
	form = BookForm()
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == 'POST':
		form = BookForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				book = form.save(commit=False)
				book.save()
				form.save_m2m()
				messages.success(request, "New book added successfully!")
				return redirect("add-new-book")

			except Exception as e:
				messages.info(request, "Please ensure to fill in valid details 1")
				return redirect("add-new-book")
		else:
			messages.info(request, "Please ensure to fill in valid details")
			return redirect("add-new-book")

	context = {'form':form,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, 'app/add-book.html', context)

@login_required(login_url="/login")
def book_detail(request, pk):
	check_if_order_has_expired()
	book = get_object_or_404(Book, id=pk)
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	context = {'item':book,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, 'app/book-detail.html', context)

@login_required(login_url="/login")
def update_book(request, pk):
	check_if_order_has_expired()
	book = get_object_or_404(Book, id=pk)
	form = BookForm(instance=book)
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == "POST":
		form = BookForm(request.POST, request.FILES, instance=book)
		if form.is_valid():
			try:
				book = form.save(commit=False)
				book.save()
				form.save_m2m()
				messages.success(request, "Book successfully updated")
				return redirect("updateBook", pk=pk)
			except Exception:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("updateBook", pk=pk)
		else:
			messages.warning(request, "Please ensure to fill in valid details")
			return redirect("updateBook", pk=pk)
	context = {'form':form,'book':book,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, 'app/update-book.html', context)

@login_required(login_url="/login")
def profile(request):
	check_if_order_has_expired()
	form = UserProfileForm()
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				nationality = form.cleaned_data.get('nationality')
				passport_no = form.cleaned_data.get('passport_no')
				image = form.cleaned_data.get('image')
				phone = form.cleaned_data.get('phone')
				UserProf = UserProfile()
				UserProf.user = request.user
				UserProf.nationality = nationality
				UserProf.passport_no = passport_no
				UserProf.image = image
				UserProf.phone = phone
				UserProf.save()
				messages.success(request, "User Profile sucessfully created!")
				return redirect("profile")

			except Exception as e:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("profile")
		else:
			messages.info(request, "Please ensure to fill in valid details")
			return redirect("profile")

	context = {'form':form,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, 'app/profile.html', context)

@login_required(login_url="/login")
def update_profile(request):
	check_if_order_has_expired()
	user_profile = get_object_or_404(UserProfile, user=request.user)
	form = UserProfileForm(instance=user_profile)
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, "User Profile sucessfully updated!")
				return redirect("update-profile")

			except Exception as e:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("update-profile")
		else:
			messages.info(request, "Please ensure to fill in valid details")
			return redirect("update-profile")

	context = {'form':form,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, 'app/update-profile.html', context)

def is_valid_queryparam(param):
	return param != '' and param is not None

@login_required(login_url="/login")
def dash_all_orders(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(ordered=True).order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset, 'page_request_var':page_request_var,
	'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders,
	 'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/all-orders.html", context)

@login_required(login_url="/login")
def dash_my_orders(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(user=request.user,ordered=True).order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset, 'page_request_var':page_request_var, 
	'processing':processing,'cancelled':cancelled,'accpted':accepted,'total_orders':total_orders,'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/my-orders.html", context)

@login_required(login_url="/login")
def dash_all_issued_books(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(ordered=True, issued=True).order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset, 'page_request_var':page_request_var, 
	'processing':processing,'cancelled':cancelled,'accpted':accepted,'total_orders':total_orders,'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/all-issued-books.html", context)

@login_required(login_url="/login")
def dash_my_issued_books(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True, issued=True).order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset,
	'processing':processing,'cancelled':cancelled,'accpted':accepted,'total_orders':total_orders,
	 'page_request_var':page_request_var, 'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/my-issued-books.html", context)

@login_required(login_url="/login")
def cancel_order(request, pk):
	check_if_order_has_expired()
	single_order = get_object_or_404(IssuedBooks, id=pk, ordered=True)
	orders = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = orders.filter(status='processing').count()
	cancelled = orders.filter(status='cancelled').count()
	accepted = orders.filter(status='accepted').count()
	total_orders = orders.count()
	if request.method == "POST":
		try:
			single_order.status = "cancelled"
			single_order.save()
			messages.success(request, "Your Order was cancelled successfully")
			return redirect("order-detail", pk=pk)
		except Exception:
			messages.error(request, "Error! Failed to cancel order")
			return redirect("order-detail", pk=pk)

	context = {'single_order':single_order,'processing':processing,'cancelled':cancelled,'accepted':accepted,'total_orders':total_orders}
	return render(request, "app/cancel-order.html", context)

@login_required(login_url="/login")
def Logout(request):
	logout(request)
	messages.success(request, "Logged out! See you soon")
	return redirect("login")

@login_required(login_url="/login")
def dash_my_expired_orders(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(user=request.user, status="expired").order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset,
	'processing':processing,'cancelled':cancelled,'accpted':accepted,'total_orders':total_orders,
	 'page_request_var':page_request_var, 'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/my-expired-orders.html", context)

@login_required(login_url="/login")
def dash_all_expired_orders(request):
	check_if_order_has_expired()
	orders = IssuedBooks.objects.filter(status="expired").order_by('-ordered_date')
	form = OrderForm()
	order_include = IssuedBooks.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
	processing = order_include.filter(status='processing').count()
	cancelled = order_include.filter(status='cancelled').count()
	accepted = order_include.filter(status='accepted').count()
	total_orders = order_include.count()
	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)
	context = {'queryset':paginated_queryset, 'page_request_var':page_request_var, 
	'processing':processing,'cancelled':cancelled,'accpted':accepted,'total_orders':total_orders,'orders':orders, 'form':form}

	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})
	return render(request, "app/all-expired-orders.html", context)

def Login(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		if request.method == "POST":
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
				messages.success(request, "Succesfully logged in as " + user.username)
				return redirect("dashboard")
			else:
				messages.info(request, "An Error occured while logging in")
				return redirect("login")
	return render(request, "app/login.html")

def register_user(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		user_form = RegisterUserForm()
		if request.method == "POST":
			user_form = RegisterUserForm(request.POST)
			if user_form.is_valid():
				try:
					user_form.save()
					messages.success(request, "Registration was succesfully completed. Kindly Login")
					return redirect("login")
				except Exception as e:
					messages.error(request,"" + type(e))
					return redirect("register-user")
	context = {'user_form':user_form}
	return render(request, "app/register.html", context)

