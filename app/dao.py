from app.models import Category, Product, User, ReceiptDetails, Receipt, Comment, Author,BookAuthor,UserRoleEnum
from app import app
import hashlib
from flask_login import current_user
from app import db
from sqlalchemy import func
import cloudinary.uploader


def load_categories():
    return Category.query.all()

def count_user_in_register():
    return db.session.query(func.count(User.id)).all()

def load_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).all()

def load_products(kw=None,cate_id=None, page=None):
     products=Product.query

     if kw:
        products=products.filter(Product.name.contains(kw))

     if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

     if page:
         page = int(page)
         page_size = app.config['PAGE_SIZE']
         start = (page - 1) * page_size
         return products.slice(start, start + page_size)

     return products.all()

def count_product():
    return Product.query.count()

def get_product_by_id(id):
    return Product.query.get(id)

def get_author_by_product_id(product_id):

    result = db.session.query(Author.name).\
        join(BookAuthor,BookAuthor.author_id.__eq__(Author.id)).\
        join(Product,BookAuthor.product_id.__eq__(Product.id)).filter(Product.id == product_id).all()

    # author=author.filter(Product.id.__eq__(1))

    return result

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def stats_revenue( thang=None, nam=None):
    # query = db.session.query(func.extract('month', Receipt.created_date),
    #                          func.sum(ReceiptDetails.quantity*ReceiptDetails.price))\
    #                   .join(ReceiptDetails, ReceiptDetails.receipt_id.__eq__(Receipt.id))\
    #                   .filter(func.extract('year', Receipt.created_date).__eq__(year))\
    #                   .group_by(func.extract('month', Receipt.created_date))
    # return query.all()
    query = db.session.query(Product.id, Product.name,func.sum(ReceiptDetails.quantity*ReceiptDetails.price),func.sum(ReceiptDetails.quantity),Category.name)\
                        .join(Category, Product.category_id.__eq__(Category.id), isouter=True)\
                        .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id))\
                      .join(Receipt, ReceiptDetails.receipt_id.__eq__(Receipt.id))


    if thang:
        query = query.filter(func.extract('year',Receipt.created_date)==nam)

    if nam:
        query = query.filter(func.extract('month',Receipt.created_date)==thang)

    return query.group_by(Product.id).order_by(-Product.id).all()


def count_product_by_cate(year=None,month=None):
    query=db.session.query(Category.id, Category.name, func.sum(ReceiptDetails.quantity*ReceiptDetails.price),func.sum(ReceiptDetails.quantity))\
             .join(Product, Product.category_id.__eq__(Category.id), isouter=True)\
            .join(ReceiptDetails,ReceiptDetails.product_id.__eq__(Product.id), isouter=True)\
             .join(Receipt,ReceiptDetails.receipt_id.__eq__(Receipt.id), isouter=True)
    if year:
        query=query.filter(func.extract('year',Receipt.created_date)==year)
    if month:
        query=query.filter(func.extract('month',Receipt.created_date)==month)
    return query.group_by(Category.id).all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def load_users_in_register():
    query = db.session.query(User.id, User.name, User.username)
    return query.all()

def save_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'],
                               receipt=r, product_id=c['id'])
            db.session.add(d)

        db.session.commit()


def register(name, username, password,avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username.strip(), password=password,avatar=avatar)
    # if avatar:
    #     res=cloudinary.uploader.upload(avatar)
    #     print(res)
    #     u.avatar=res['secure_url']
    db.session.add(u)
    db.session.commit()

def create_employee(name, username, password,avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username.strip(), password=password,avatar=avatar,user_role=UserRoleEnum.EMPLOYEE)
    db.session.add(u)
    db.session.commit()

def get_comments_by_product(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).all()



def add_comment(product_id, content):
    c = Comment(product_id=product_id, content=content, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c

if __name__ == '__main__':
    from app import app
    with app.app_context():
        # result = db.session.query(Category.name, func.sum(ReceiptDetails.quantity*ReceiptDetails.price)) \
        #         .join(Product, Category.id == Product.category_id) \
        #         .join(ReceiptDetails, Product.id == ReceiptDetails.product_id) \
        #         .join(Receipt, ReceiptDetails.receipt_id == Receipt.id) \
        #         .filter(func.extract('month', Receipt.created_date) == 1) \
        #          .group_by(Category.id) \
        #         .all()
        # print(result)
        print(count_product_by_cate(2024,1))
