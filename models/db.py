from extensions import db

from sqlalchemy.dialects.mysql import LONGBLOB

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(LONGBLOB)  # This column will be created as LONGBLOB in MySQL

    def __repr__(self):
        return f'<Product {self.name}>'


class AdvertisementTargeting(db.Model):
    __tablename__ = 'advertisement_targeting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    targeted_audience = db.Column(db.String(100))
    targeted_gender = db.Column(db.String(50))
    keyword = db.Column(db.JSON)
    counter = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<AdvertisementTargeting for product_id {self.product_id}>'
