import enum
from enum import unique

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from app import app, db
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Enum, DateTime
from datetime import datetime
import hashlib


class UserRoleEnum(enum.Enum):
    USER = 1
    ADMIN = 2
    EMPLOYEE = 3


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    name = Column(String(50), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dsvtzkvti/image/upload/v1731028204/edjgfxdm4i8rnaszyz1x.png')
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = 'category'

    name = Column(String(50), nullable=True)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Product(BaseModel):
    __tablename__ = 'product'

    name = Column(String(255), nullable=True)
    price = Column(Float, default=0)
    image = Column(String(100),
                   default='https://res.cloudinary.com/dsvtzkvti/image/upload/v1731028642/awm6x6povtt2cixutbad.jpg')
    quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    receipt_details = relationship('ReceiptDetails', backref='product', lazy=True)
    book_author = relationship('BookAuthor', backref='product', lazy=True)
    comments = relationship('Comment', backref='product', lazy=True)

    def __str__(self):
        return self.name


class Author(BaseModel):
    __tablename__ = 'author'

    name = Column(String(50), nullable=True)
    biography = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    birthday = Column(DateTime, nullable=True)
    book_author = relationship('BookAuthor', backref='author', lazy=True)

    def __str__(self):
        return self.name


class BookAuthor(BaseModel):
    __tablename__ = 'book_author'

    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    author_id = Column(Integer, ForeignKey(Author.id), nullable=False)


class Receipt(BaseModel):
    __tablename__ = 'receipt'

    status = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetails', backref='receipt', lazy=True)


class ReceiptDetails(BaseModel):
    __tablename__ = 'receipt_details'

    quantity = Column(Integer, default=0)
    price = Column(Float, default=0)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)


class Comment(BaseModel):
    __tablename__ = 'comment'

    content = Column(String(255), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        c1 = Category(name='Sách pháp luật')
        c2 = Category(name='Sách thiếu nhi')
        c3 = Category(name='Sách khoa học')
        c4 = Category(name='Sách ngoại ngữ')
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

        products = [{
            "id": 1,
            "name": "Bài Tập Giáo Dục Kinh Tế Và Pháp Luật 12",
            "price": 17500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731030498/g6wsgnaka7ycusdcef2a.png",
            "quantity": 10,
            "category_id": 1
        }, {
            "id": 2,
            "name": "Quy Định Pháp Luật Về Cơ Chế, Chính Sách Hỗ Trợ Sản Xuất Nông Nghiệp Để Khôi Phục Sản Xuất Vùng Bị Thiệt Hại Do Thiên Tai, Dịch Bệnh",
            "price": 20500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731046959/qycfemeqcactndq2hlqw.png",
            "quantity": 15,
            "category_id": 1
        }, {
            "id": 3,
            "name": "Chính Sách Pháp Luật Tố Tụng Dân Sự Đáp Ứng Yêu Cầu Của Cuộc Cách Mạng Công Nghiệp Lần Thứ Tư Ở Việt Nam",
            "price": 21500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731047084/icbntpxoojpbtcqvblud.png",
            "quantity": 20,
            "category_id": 1
        }, {
            "id": 4,
            "name": "Doraemon - Tranh Truyện Màu - Năm 2112 Doraemon",
            "price": 21500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731047233/kdxtuohscmpe5k4bu6n1.png",
            "quantity": 20,
            "category_id": 2
        }, {
            "id": 5,
            "name": "Doraemon - Tranh Truyện Màu - Năm 2112 Doraemon",
            "price": 21500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731047367/ehmmkyj6ht1gheiomtmi.png",
            "quantity": 20,
            "category_id": 2
        }, {
            "id": 6,
            "name": "Cuốn Sách Khoa Học Đầu Tiên Dành Cho Học Sinh Tiểu Học - Câu Chuyện Về Biến Đổi Khí Hậu",
            "price": 21500,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731047458/jtb3n5tsffhkpb6fm7us.png",
            "quantity": 20,
            "category_id": 3
        }, {
            "id": 7,
            "name": "Giáo Trình Chuẩn HSK 5 - Sách Bài Tập - Tập 1",
            "price": 150000,
            "image": "https://res.cloudinary.com/dsvtzkvti/image/upload/v1731047559/xcbi4dpirjuln1pxbheq.png",
            "quantity": 20,
            "category_id": 4
        }]

        for p in products:
            prod = Product(**p)
            db.session.add(prod)

        db.session.commit()

        u = User(name='Admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.ADMIN)
        db.session.add(u)
        db.session.commit()