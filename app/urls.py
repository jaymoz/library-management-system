from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path("logout/", views.Logout, name="logout"),
    path("login/", views.Login, name="login"),
    path("register/", views.register_user, name="register-user"),
    path('cart/',views.cart, name="cart"),
	path('add-to-cart/<slug>/',views.add_to_cart, name='add'),
	path('remove-from-cart/<slug>/',views.remove_from_cart, name='remove'),
	path('remove-item-from-cart/<slug>/',views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
	path('add-to-cart-page/<slug>/',views.add_to_cart_page, name='add-to-cart-page'),
	path('remove-from-cart-page/<slug>/',views.remove_from_cart_page, name='remove-from-cart-page'),
	path('remove-item-from-cart-page/<slug>/',views.remove_single_item_from_cart_page, name='remove-single-item-from-cart-page'),
	path('book-detail/<str:pk>/', views.book_detail, name='book-detail'),
    path('dashboard/',  views.dashboard, name = 'dashboard'),
    path('order-detail/<str:pk>/', views.order_detail, name='order-detail'),
    path('add-book/',views.add_book, name="add-new-book"),
    path('update-book/<str:pk>/', views.update_book, name="updateBook"),
    path('delete-book/<str:pk>/', views.delete_book, name="deleteBook"),
    path("all-books/", views.all_books, name="allBooks"),
    path("all-orders", views.dash_all_orders, name="allOrders"),
    path("my-orders/", views.dash_my_orders, name="myOrders"),
    path("all-issued-books", views.dash_all_issued_books, name="AllIssued"),
    path("my-issued-books/", views.dash_my_issued_books, name="myIssued"),
    path("all-expired-orders/", views.dash_all_expired_orders, name="allExpired"),
    path("my-expired-books/", views.dash_my_expired_orders, name="myExpired"),
    path("cancel-order/<str:pk>/", views.cancel_order, name="cancel-order"),
    path("profile", views.profile, name="profile"), 
    path('update-profile/',views.update_profile, name='update-profile'),
    path('contact-admin/', views.message, name='message')
]