"""
Data generation service using Python Faker to create realistic test data.
"""

import logging
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any
from faker import Faker

from ..models import User, Product, Order, Review, OrderItem
from ..config import settings

logger = logging.getLogger(__name__)


class DataGenerator:
    """Service for generating realistic test data using Python Faker."""
    
    def __init__(self):
        self.faker = Faker()
        self.random = random.Random()
        
        # Product categories and brands for realistic data
        self.categories = [
            "Electronics", "Clothing", "Books", "Home & Kitchen", "Sports & Outdoors",
            "Beauty & Personal Care", "Automotive", "Toys & Games", "Health & Wellness", "Food & Grocery"
        ]
        
        self.brands_by_category = {
            "Electronics": ["Apple", "Samsung", "Sony", "LG", "Dell", "HP", "Lenovo", "Microsoft"],
            "Clothing": ["Nike", "Adidas", "Zara", "H&M", "Levi's", "Gap", "Uniqlo", "Puma"],
            "Books": ["Penguin", "Harper Collins", "Simon & Schuster", "Random House", "Macmillan"],
            "Home & Kitchen": ["KitchenAid", "Cuisinart", "Hamilton Beach", "Black & Decker", "Instant Pot"],
            "Sports & Outdoors": ["Under Armour", "Reebok", "Columbia", "The North Face", "Patagonia"],
            "Beauty & Personal Care": ["L'Oreal", "Maybelline", "Clinique", "MAC", "Neutrogena"],
            "Automotive": ["Bosch", "Mobil 1", "Castrol", "Michelin", "Goodyear"],
            "Toys & Games": ["LEGO", "Mattel", "Hasbro", "Fisher-Price", "Playmobil"],
            "Health & Wellness": ["Johnson & Johnson", "Pfizer", "Bayer", "Tylenol", "Advil"],
            "Food & Grocery": ["Kraft", "Nestle", "General Mills", "Kellogg's", "Campbell's"],
        }
    
    def generate_users(self, count: int) -> List[User]:
        """Generate a list of fake users."""
        logger.info(f"Generating {count} users")
        users = []
        
        for _ in range(count):
            # Random date of birth between 18 and 80 years ago
            birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=80)
            
            # Registration date in the past 5 years
            registration_date = self.faker.date_time_between(start_date='-5y', end_date='now')
            
            user = User(
                username=self.faker.user_name(),
                email=self.faker.email(),
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                date_of_birth=birth_date,
                registration_date=registration_date,
                is_active=self.faker.boolean(chance_of_getting_true=90),
                address=self.faker.address().replace('\n', ', '),
                phone=self.faker.phone_number()
            )
            users.append(user)
        
        logger.info(f"Generated {len(users)} users")
        return users
    
    def generate_products(self, count: int) -> List[Product]:
        """Generate a list of fake products."""
        logger.info(f"Generating {count} products")
        products = []
        
        for _ in range(count):
            category = self.random.choice(self.categories)
            brands = self.brands_by_category[category]
            brand = self.random.choice(brands)
            
            # Generate realistic product names based on category
            name = self._generate_product_name(category)
            
            # Generate realistic prices based on category
            price = self._generate_price_for_category(category)
            
            # Created date in the past 2 years
            created_date = self.faker.date_time_between(start_date='-2y', end_date='now')
            
            product = Product(
                name=name,
                description=self.faker.text(max_nb_chars=200),
                price=price,
                category=category,
                brand=brand,
                sku=self._generate_sku(),
                stock_quantity=self.faker.random_int(min=0, max=1000),
                created_date=created_date,
                is_active=self.faker.boolean(chance_of_getting_true=95)
            )
            products.append(product)
        
        logger.info(f"Generated {len(products)} products")
        return products
    
    def generate_orders(self, users: List[User], products: List[Product], max_orders_per_user: int) -> List[Order]:
        """Generate fake orders for given users and products."""
        logger.info(f"Generating orders for {len(users)} users (max {max_orders_per_user} orders per user)")
        orders = []
        
        for user in users:
            num_orders = self.faker.random_int(min=0, max=max_orders_per_user)
            
            for _ in range(num_orders):
                # Order date between user registration and now
                min_date = user.registration_date
                max_date = datetime.now()
                if min_date >= max_date:
                    order_date = min_date
                else:
                    order_date = self.faker.date_time_between(start_date=min_date, end_date=max_date)
                
                # Generate realistic order total
                total_amount = Decimal(str(self.faker.random.uniform(10.0, 500.0))).quantize(Decimal('0.01'))
                
                order = Order(
                    user_id=user.user_id,
                    order_date=order_date,
                    status=self._generate_order_status(),
                    total_amount=total_amount,
                    shipping_address=user.address,
                    payment_method=self._generate_payment_method()
                )
                orders.append(order)
        
        logger.info(f"Generated {len(orders)} orders")
        return orders
    
    def generate_reviews(self, users: List[User], products: List[Product], max_reviews_per_product: int) -> List[Review]:
        """Generate fake reviews for given products and users."""
        logger.info(f"Generating reviews for {len(products)} products (max {max_reviews_per_product} reviews per product)")
        reviews = []
        
        for product in products:
            num_reviews = self.faker.random_int(min=0, max=max_reviews_per_product)
            
            # Select random users for reviews (avoid duplicates for same product)
            available_users = users.copy()
            self.random.shuffle(available_users)
            reviewers = available_users[:min(num_reviews, len(available_users))]
            
            for user in reviewers:
                # Rating between 1-5, with bias towards higher ratings
                rating = self._generate_rating()
                
                # Review date after product creation
                min_date = product.created_date
                max_date = datetime.now()
                if min_date >= max_date:
                    review_date = min_date
                else:
                    review_date = self.faker.date_time_between(start_date=min_date, end_date=max_date)
                
                review = Review(
                    product_id=product.product_id,
                    user_id=user.user_id,
                    rating=rating,
                    title=self._generate_review_title(rating),
                    comment=self._generate_review_comment(rating),
                    review_date=review_date,
                    is_verified_purchase=self.faker.boolean(chance_of_getting_true=70)
                )
                reviews.append(review)
        
        logger.info(f"Generated {len(reviews)} reviews")
        return reviews
    
    def generate_order_items(self, orders: List[Order], products: List[Product]) -> List[OrderItem]:
        """Generate order items for each order."""
        logger.info(f"Generating order items for {len(orders)} orders")
        order_items = []
        
        for order in orders:
            # Each order has 1-5 items
            num_items = self.faker.random_int(min=1, max=5)
            selected_products = self.random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = self.faker.random_int(min=1, max=3)
                # Use product price with slight variation
                variation = Decimal(str(self.faker.random.uniform(0.9, 1.1))).quantize(Decimal('0.01'))
                unit_price = (product.price * variation).quantize(Decimal('0.01'))
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=unit_price
                )
                order_items.append(order_item)
        
        logger.info(f"Generated {len(order_items)} order items")
        return order_items
    
    # Helper methods for generating realistic data
    
    def _generate_product_name(self, category: str) -> str:
        """Generate a product name based on category."""
        if category == "Electronics":
            return self.faker.random_element(["Smart TV", "Laptop", "Smartphone", "Tablet", "Headphones", "Camera", "Gaming Console"])
        elif category == "Clothing":
            return self.faker.random_element(["T-Shirt", "Jeans", "Sneakers", "Jacket", "Dress", "Shirt", "Pants"])
        elif category == "Books":
            return self.faker.catch_phrase()  # Use catch phrase as book title
        elif category == "Home & Kitchen":
            return self.faker.random_element(["Blender", "Coffee Maker", "Microwave", "Toaster", "Cookware Set", "Vacuum Cleaner"])
        else:
            return self.faker.catch_phrase()
    
    def _generate_sku(self) -> str:
        """Generate a realistic SKU."""
        return f"{self.faker.random_letter().upper()}{self.faker.random_letter().upper()}{self.faker.random_letter().upper()}-{self.faker.random_number(digits=4)}"
    
    def _generate_price_for_category(self, category: str) -> Decimal:
        """Generate a realistic price based on category."""
        price_ranges = {
            "Electronics": (50, 2000),
            "Clothing": (15, 200),
            "Books": (8, 50),
            "Home & Kitchen": (20, 300),
            "Sports & Outdoors": (25, 500),
            "Beauty & Personal Care": (10, 100),
            "Automotive": (20, 200),
            "Toys & Games": (15, 150),
            "Health & Wellness": (10, 80),
            "Food & Grocery": (5, 50),
        }
        
        min_price, max_price = price_ranges.get(category, (10, 100))
        price = self.faker.random.uniform(min_price, max_price)
        return Decimal(str(price)).quantize(Decimal('0.01'))
    
    def _generate_order_status(self) -> str:
        """Generate a realistic order status."""
        return self.faker.random_element(["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"])
    
    def _generate_payment_method(self) -> str:
        """Generate a realistic payment method."""
        return self.faker.random_element(["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Google Pay", "Bank Transfer"])
    
    def _generate_rating(self) -> int:
        """Generate a rating with bias towards higher ratings."""
        # Bias towards higher ratings (more realistic for e-commerce)
        ratings = [1, 2, 3, 4, 4, 5, 5, 5]  # Higher probability for 4s and 5s
        return self.random.choice(ratings)
    
    def _generate_review_title(self, rating: int) -> str:
        """Generate a review title based on rating."""
        if rating >= 4:
            return self.faker.random_element([
                "Great product!", "Love it!", "Excellent quality", 
                "Highly recommend", "Perfect!", "Amazing purchase"
            ])
        elif rating == 3:
            return self.faker.random_element([
                "It's okay", "Average product", "Could be better", 
                "Mixed feelings", "Decent for the price"
            ])
        else:
            return self.faker.random_element([
                "Disappointed", "Not as expected", "Poor quality", 
                "Would not recommend", "Waste of money"
            ])
    
    def _generate_review_comment(self, rating: int) -> str:
        """Generate a review comment based on rating."""
        if rating >= 4:
            return self.faker.random_element([
                "This product exceeded my expectations. Great quality and fast shipping!",
                "I'm very satisfied with this purchase. Works exactly as described.",
                "Excellent value for money. Would definitely buy again.",
                "Perfect product! Easy to use and great build quality.",
                "Outstanding quality and design. Highly recommended!"
            ])
        elif rating == 3:
            return self.faker.random_element([
                "The product is decent but nothing special. Does what it's supposed to do.",
                "It's okay for the price, but I've seen better quality elsewhere.",
                "Average product. Some good points and some not so good.",
                "Works as expected but could be improved in some areas."
            ])
        else:
            return self.faker.random_element([
                "Product quality was much lower than expected. Not satisfied with this purchase.",
                "Broke after just a few uses. Very disappointed.",
                "Not worth the money. Would not recommend to others.",
                "Poor build quality and doesn't work as advertised."
            ])


# Global data generator instance
data_generator = DataGenerator()