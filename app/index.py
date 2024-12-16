import math

from flask import Flask, render_template, request, redirect,session,jsonify
import dao, utils
from app import app,login,controllers
from flask_login import login_user,logout_user
from app.models import Category, Product, User




app.add_url_rule('/', 'index', controllers.index)
app.add_url_rule('/products/<int:id>', 'detail', controllers.detail)
app.add_url_rule('/admin/login', 'login-admin', controllers.login_admin, methods=['post'])
app.add_url_rule('/login', 'login-user', controllers.login_my_user, methods=['get', 'post'])
app.add_url_rule('/cart', 'cart', controllers.cart)
app.add_url_rule('/api/cart', 'add-cart', controllers.add_to_cart, methods=['post'])
app.add_url_rule('/api/cart/<product_id>', 'update-cart', controllers.update_cart, methods=['put'])
app.add_url_rule('/api/cart/<product_id>', 'delete-cart', controllers.delete_cart, methods=['delete'])
app.add_url_rule('/api/pay', 'pay', controllers.pay)
app.add_url_rule('/register', 'register', controllers.register, methods=['get', 'post'])
app.add_url_rule('/logout', 'logout', controllers.logout_my_user)
app.add_url_rule('/cashier', 'cashier', controllers.cashier)
app.add_url_rule('/api/cartCashier', 'add-cart-cashier', controllers.add_to_cart_emp, methods=['post'])
app.add_url_rule('/api/cartCashier/<product_id>', 'update-cart-cashier', controllers.update_cart_emp, methods=['put'])
app.add_url_rule('/api/cartCashier/<product_id>', 'delete-cart-cashier', controllers.delete_cart_emp, methods=['delete'])
app.add_url_rule('/api/payCashier', 'pay-cashier', controllers.pay_emp)
app.add_url_rule('/api/printBill', 'print-bill', controllers.print_bill)
app.add_url_rule('/api/products/<id>/comments', 'comment-add', controllers.add_comment, methods=['post'])




@login.user_loader
def get_user_by_id(user_id):
    return User.query.get(user_id)

@app.context_processor
def common_responses():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.cart_stats(session.get('cart')),
        'cashier_stats':utils.cart_stats(session.get('cartCashier')),
        'print_cart_stats':utils.cart_stats(session.get('print_cart'))
    }



if __name__=='__main__':
    from app import admin
    app.run(debug=True)
