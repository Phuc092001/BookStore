import hashlib
import json
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from wtforms import TextAreaField, form, StringField
from wtforms.widgets import TextArea
from app import app, db
from app.models import Category, Product, UserRoleEnum, Author, BookAuthor, Receipt, ReceiptDetails,User
from flask_login import logout_user, current_user
from flask import redirect, request, flash, url_for
import dao
from wtforms.validators import ValidationError
from wtforms import IntegerField
from flask_admin.form import rules
from wtforms import validators
import cloudinary.uploader
from datetime import datetime, timedelta


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedAdmin1(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class MyProductView(AuthenticatedAdmin):
    with open("data/quy_dinh.json", "r") as file:
        quy_dinh = json.load(file)
        column_list = ['id', 'name', 'price', 'category', 'quantity']
        column_searchable_list = ['name']
        column_filters = ['name', 'price']
        column_editable_list = ['name', 'price']
        form_excluded_columns = ('receipt_details', 'active', 'book_author', 'comments')
        min_sach = int(quy_dinh["so_sach_toi_thieu"])
        max_sach = int(quy_dinh["so_sach_toi_da"])
        form_extra_fields = {
            'quantity': IntegerField('Quantity', validators=[validators.NumberRange(min=min_sach, max=max_sach)])
        }
        edit_modal = True
        column_labels = {
            'name': 'Tên sản phẩm',
            # 'price': 'Gía',
            'author_name': 'Tác giả',
            'quantity': 'Số lượng',
            'category': 'Loại'
        }
        extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
        form_overrides = {
            'description': CKTextAreaField
        }


class MyAuthorView(AuthenticatedAdmin):
    column_list = ['name', 'biography', 'country', 'birthday']
    form_excluded_columns = ('book_author')
    edit_modal = True
    column_labels = {
        'name': 'Tên tác giả',
        'biography': 'Tiểu sử',
        'country': 'Quốc gia',
        'birthday': 'Sinh nhật'
    }


class MyBookAuthorView(AuthenticatedAdmin):
    column_list = ['product', 'author']
    column_filters = ['product', 'author']
    edit_modal = True
    column_labels = {
        'product_id': 'Tên sách',
        'author_id': 'Tác giả'
    }


class MyReceiptView(AuthenticatedAdmin):
    column_list = ['id', 'user_id', 'created_date', 'status']
    form_excluded_columns = ('receipt_details')
    can_create = False
    edit_modal = True


class MyReceiptDetailView(AuthenticatedAdmin):
    column_list = ['product_id', 'receipt_id', 'price', 'quantity']
    can_create = False


class CustomView(AuthenticatedAdmin1):
    @expose('/')
    def index(self):
        with open("data/quy_dinh.json", "r") as file:
            quy_dinh = json.load(file)
        don_hang_chua_giao = Receipt.query.filter_by(status=False).all()
        ma_don_chua_giao = []
        for don_hang in don_hang_chua_giao:
            thoi_gian_tao_don = don_hang.created_date
            thoi_gian_hien_tai = datetime.now()
            thoi_gian_tao_don_da_qua_gio_quy_định = thoi_gian_tao_don + timedelta(hours=int(quy_dinh["gio_huy_don"]))

            if thoi_gian_hien_tai > thoi_gian_tao_don_da_qua_gio_quy_định:
                ma_don_chua_giao.append(don_hang.id)

        if len(ma_don_chua_giao) > 0:
            return self.render('admin/custom_message.html', array=ma_don_chua_giao, gio=int(quy_dinh["gio_huy_don"]))
        else:
            return self.render('admin/custom_message.html', message=int(quy_dinh["gio_huy_don"]))


class MyCategoryView(AuthenticatedAdmin):
    column_list = ['id', 'name', 'products']
    form_excluded_columns = ('products')


class StatsView(AuthenticatedAdmin1):
    @expose('/')
    def index(self):
        nam = request.args.get('year')
        thang = request.args.get('month')
        stats = dao.stats_revenue(
            nam=request.args.get('year'),
            thang=request.args.get('month')
        )

        return self.render('admin/stats.html', stats=stats, nam1=nam, thang1=thang)


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        thang = request.args.get('month')
        nam = request.args.get('year')
        stats = dao.count_product_by_cate(year=request.args.get('year'), month=request.args.get('month'))

        return self.render('admin/index.html', stats=stats, thang=thang, nam=nam)


class MyRuleView(AuthenticatedAdmin1):
    @expose('/', methods=['get', 'post'])
    def quy_dinh(self):
        err_msg = ""
        with open("data/quy_dinh.json", "r") as file:
            quy_dinh = json.load(file)

        with open("data/quy_dinh.json", "w") as file:
            if request.method.__eq__("POST"):
                so_sach_toi_thieu = request.form["so_sach_toi_thieu"]
                so_sach_toi_da = request.form["so_sach_toi_da"]
                so_gio_huy_don = request.form["gio_huy_don"]
                # file.write(json.dumps(quy_dinh))
                if so_sach_toi_thieu and so_sach_toi_da and so_gio_huy_don:
                    if int(so_sach_toi_thieu) < 150 or int(so_sach_toi_da) > 300:
                        err_msg = "Số sách tối thiểu là 150 và số sách tối đa chỉ là 300"
                        file.write(json.dumps(quy_dinh))
                        return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)
                    elif int(so_gio_huy_don) < 24:
                        err_msg = "Số giờ hủy đơn ít nhất 24h"
                        file.write(json.dumps(quy_dinh))
                        return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)
                    else:
                        quy_dinh["so_sach_toi_thieu"] = so_sach_toi_thieu
                        quy_dinh["so_sach_toi_da"] = so_sach_toi_da
                        quy_dinh["gio_huy_don"] = so_gio_huy_don
                        file.write(json.dumps(quy_dinh))
                        return self.render("admin/rule.html", quy_dinh=quy_dinh, err_msg=err_msg)
                else:
                    err_msg = "Chưa nhập đủ"
                    file.write(json.dumps(quy_dinh))
            file.write(json.dumps(quy_dinh))
        return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)


class LogoutView(AuthenticatedAdmin1):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')


admin = Admin(app=app, name='Management', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(MyReceiptView(Receipt, db.session, name='Receipt'))
admin.add_view(MyCategoryView(Category, db.session, name='Type'))
admin.add_view(MyProductView(Product, db.session, name='Book'))
admin.add_view(MyAuthorView(Author, db.session, name='Author'))
admin.add_view(MyBookAuthorView(BookAuthor, db.session, name='Author and Book'))
admin.add_view(MyReceiptDetailView(ReceiptDetails, db.session, name='Receipt Detail'))
admin.add_view(MyRuleView(name="Rule"))
admin.add_view(CustomView(name='Check Receipt'))
admin.add_view(StatsView(name='Statistic'))
admin.add_view(LogoutView(name='Log out'))