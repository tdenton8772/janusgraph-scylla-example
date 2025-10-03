#!/usr/bin/env python3
"""
E-commerce Demo Application - JanusGraph with ScyllaDB
This application demonstrates the differences between graph-based and CQL-based access patterns.
"""

import logging
import time
import sys
from typing import List, Dict, Any

import click
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Import our application modules
from ecommerce.config import settings
from ecommerce.services.database import db_manager
from ecommerce.services.data_generator import data_generator
from ecommerce.queries.graph_queries import graph_service
from ecommerce.queries.cql_queries import cql_service

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.app.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ECommerceDemo:
    """Main demo application class."""
    
    def __init__(self):
        self.users = []
        self.products = []
        self.orders = []
        self.order_items = []
        self.reviews = []
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{title:^60}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{Fore.YELLOW}{'-'*40}")
        print(f"{Fore.YELLOW}{title}")
        print(f"{Fore.YELLOW}{'-'*40}{Style.RESET_ALL}")
    
    def setup_databases(self):
        """Initialize database connections and schemas."""
        self.print_section("Setting up databases...")
        
        try:
            # Connect to both databases
            db_manager.connect_all()
            
            # Setup keyspaces
            db_manager.setup_keyspaces()
            
            # Setup CQL schema
            db_manager.setup_cql_schema()
            
            # Initialize JanusGraph schema
            graph_service.initialize_schema()
            
            print(f"{Fore.GREEN}✓ Database setup complete")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Database setup failed: {e}")
            raise
    
    def generate_test_data(self):
        """Generate test data using Faker."""
        self.print_section("Generating test data...")
        
        # Generate users
        self.users = data_generator.generate_users(settings.app.num_users)
        print(f"Generated {len(self.users)} users")
        
        # Generate products
        self.products = data_generator.generate_products(settings.app.num_products)
        print(f"Generated {len(self.products)} products")
        
        # Generate orders
        self.orders = data_generator.generate_orders(
            self.users, self.products, settings.app.max_orders_per_user
        )
        print(f"Generated {len(self.orders)} orders")
        
        # Generate order items
        self.order_items = data_generator.generate_order_items(self.orders, self.products)
        print(f"Generated {len(self.order_items)} order items")
        
        # Generate reviews
        self.reviews = data_generator.generate_reviews(
            self.users, self.products, settings.app.max_reviews_per_product
        )
        print(f"Generated {len(self.reviews)} reviews")
        
        print(f"{Fore.GREEN}✓ Test data generation complete")
    
    def load_data_to_graph(self):
        """Load data into JanusGraph."""
        self.print_section("Loading data to JanusGraph...")
        
        start_time = time.time()
        
        # Load vertices
        user_count = sum(graph_service.insert_user(user) for user in self.users)
        product_count = sum(graph_service.insert_product(product) for product in self.products)
        order_count = sum(graph_service.insert_order(order) for order in self.orders)
        review_count = sum(graph_service.insert_review(review) for review in self.reviews)
        
        # Create edges
        edge_count = 0
        for order in self.orders:
            if graph_service.create_user_order_edge(order.user_id, order.order_id):
                edge_count += 1
        
        for review in self.reviews:
            if graph_service.create_user_review_edge(review.user_id, review.review_id):
                edge_count += 1
            if graph_service.create_product_review_edge(review.product_id, review.review_id):
                edge_count += 1
        
        end_time = time.time()
        
        print(f"Loaded {user_count} users, {product_count} products, {order_count} orders, {review_count} reviews")
        print(f"Created {edge_count} edges")
        print(f"Graph loading took {end_time - start_time:.2f} seconds")
        print(f"{Fore.GREEN}✓ JanusGraph data loading complete")
    
    def load_data_to_cql(self):
        """Load data into ScyllaDB via CQL."""
        self.print_section("Loading data to ScyllaDB (CQL)...")
        
        start_time = time.time()
        
        # Load data to CQL tables
        user_count = sum(cql_service.insert_user(user) for user in self.users)
        product_count = sum(cql_service.insert_product(product) for product in self.products)
        order_count = sum(cql_service.insert_order(order) for order in self.orders)
        order_item_count = sum(cql_service.insert_order_item(item) for item in self.order_items)
        review_count = sum(cql_service.insert_review(review) for review in self.reviews)
        
        end_time = time.time()
        
        print(f"Loaded {user_count} users, {product_count} products, {order_count} orders")
        print(f"Loaded {order_item_count} order items, {review_count} reviews")
        print(f"CQL loading took {end_time - start_time:.2f} seconds")
        print(f"{Fore.GREEN}✓ ScyllaDB (CQL) data loading complete")
    
    def demonstrate_access_patterns(self):
        """Demonstrate different access patterns between graph and CQL."""
        self.print_header("ACCESS PATTERN DEMONSTRATIONS")
        
        if not self.users or not self.products:
            print(f"{Fore.RED}No test data available. Run data generation first.")
            return
        
        # Select sample data for demos
        sample_user = self.users[0]
        sample_product = self.products[0]
        
        print(f"Using sample user: {sample_user.username} ({sample_user.user_id})")
        print(f"Using sample product: {sample_product.name} ({sample_product.product_id})")
        
        # Demo 1: User Order History
        self._demo_user_orders(sample_user.user_id)
        
        # Demo 2: Product Reviews
        self._demo_product_reviews(sample_product.product_id)
        
        # Demo 3: Product Recommendations (Graph-specific)
        self._demo_product_recommendations(sample_user.user_id)
        
        # Demo 4: Category Browsing
        self._demo_category_browsing(sample_product.category)
        
        # Demo 5: Complex Graph Traversals
        self._demo_complex_traversals()
    
    def _demo_user_orders(self, user_id):
        """Demonstrate user order retrieval in both systems."""
        self.print_section("Demo 1: User Order History")
        
        print(f"{Fore.BLUE}Graph Query (JanusGraph + Gremlin):")
        start_time = time.time()
        graph_orders = graph_service.get_user_orders(user_id, limit=5)
        graph_time = time.time() - start_time
        print(f"Found {len(graph_orders)} orders in {graph_time:.3f}s")
        if graph_orders:
            print(f"Sample order: {graph_orders[0]}")
        
        print(f"\n{Fore.BLUE}CQL Query (Direct ScyllaDB):")
        start_time = time.time()
        cql_orders = cql_service.get_user_orders(user_id, limit=5)
        cql_time = time.time() - start_time
        print(f"Found {len(cql_orders)} orders in {cql_time:.3f}s")
        if cql_orders:
            print(f"Sample order: {cql_orders[0]}")
        
        print(f"\n{Fore.MAGENTA}Analysis:")
        print(f"• Graph query uses traversal: user -> out('placed_order')")
        print(f"• CQL query uses optimized table: user_orders partitioned by user_id")
        print(f"• CQL is typically faster for this simple lookup pattern")
    
    def _demo_product_reviews(self, product_id):
        """Demonstrate product review retrieval in both systems."""
        self.print_section("Demo 2: Product Reviews")
        
        print(f"{Fore.BLUE}Graph Query (JanusGraph + Gremlin):")
        start_time = time.time()
        graph_reviews = graph_service.get_product_reviews(product_id, limit=5)
        graph_time = time.time() - start_time
        print(f"Found {len(graph_reviews)} reviews in {graph_time:.3f}s")
        if graph_reviews:
            print(f"Sample review: {graph_reviews[0]}")
        
        print(f"\n{Fore.BLUE}CQL Query (Direct ScyllaDB):")
        start_time = time.time()
        cql_reviews = cql_service.get_product_reviews(product_id, limit=5)
        cql_time = time.time() - start_time
        print(f"Found {len(cql_reviews)} reviews in {cql_time:.3f}s")
        if cql_reviews:
            print(f"Sample review: {cql_reviews[0]}")
        
        print(f"\n{Fore.MAGENTA}Analysis:")
        print(f"• Graph query uses traversal: product -> out('has_review')")
        print(f"• CQL query uses table partitioned by product_id")
        print(f"• Both approaches perform well for this access pattern")
    
    def _demo_product_recommendations(self, user_id):
        """Demonstrate product recommendations - graph excels here."""
        self.print_section("Demo 3: Product Recommendations (Graph Advantage)")
        
        print(f"{Fore.BLUE}Graph Query (JanusGraph + Gremlin):")
        print("Complex traversal: user -> orders -> other_users -> their_orders -> products")
        start_time = time.time()
        recommendations = graph_service.get_product_recommendations(user_id, limit=5)
        graph_time = time.time() - start_time
        print(f"Found {len(recommendations)} recommendations in {graph_time:.3f}s")
        if recommendations:
            print(f"Sample recommendation: {recommendations[0]}")
        
        print(f"\n{Fore.BLUE}CQL Equivalent:")
        print("Would require multiple queries and application-level joins:")
        print("1. Get user's orders")
        print("2. For each order, get other users who ordered same products")
        print("3. Get products those users also ordered")
        print("4. Filter and rank results")
        print("This is complex and inefficient with CQL alone.")
        
        print(f"\n{Fore.MAGENTA}Analysis:")
        print(f"• Graph databases excel at multi-hop relationship queries")
        print(f"• Single Gremlin traversal vs multiple CQL queries + application logic")
        print(f"• Graph approach is more intuitive for recommendation algorithms")
    
    def _demo_category_browsing(self, category):
        """Demonstrate category-based product browsing."""
        self.print_section("Demo 4: Category Browsing")
        
        print(f"Browsing category: {category}")
        
        print(f"\n{Fore.BLUE}Graph Query (JanusGraph + Gremlin):")
        print("Filter vertices by category property")
        # For simplicity, we won't implement this specific graph query
        print("Graph approach would filter product vertices by category property")
        
        print(f"\n{Fore.BLUE}CQL Query (Direct ScyllaDB):")
        start_time = time.time()
        products = cql_service.get_products_by_category(category, limit=5)
        cql_time = time.time() - start_time
        print(f"Found {len(products)} products in {cql_time:.3f}s")
        if products:
            print(f"Sample product: {products[0]}")
        
        print(f"\n{Fore.MAGENTA}Analysis:")
        print(f"• CQL excels with dedicated products_by_category table")
        print(f"• Optimized for category browsing with proper partitioning")
        print(f"• Graph would require filtering, less efficient for this pattern")
    
    def _demo_complex_traversals(self):
        """Demonstrate complex graph traversals that would be difficult in CQL."""
        self.print_section("Demo 5: Complex Graph Analysis")
        
        print(f"{Fore.BLUE}Social Network Analysis:")
        if self.users:
            sample_user_id = self.users[0].user_id
            start_time = time.time()
            network = graph_service.get_user_social_network(sample_user_id)
            graph_time = time.time() - start_time
            print(f"Analyzed social network in {graph_time:.3f}s")
            print(f"User has {network.get('connection_count', 0)} connections through shared purchases")
        
        print(f"\n{Fore.BLUE}Product Popularity Analysis:")
        start_time = time.time()
        trends = graph_service.analyze_product_popularity_trends()
        graph_time = time.time() - start_time
        print(f"Analyzed popularity trends in {graph_time:.3f}s")
        print(f"Found {len(trends)} trending products")
        if trends:
            print(f"Most popular: {trends[0]}")
        
        print(f"\n{Fore.MAGENTA}Analysis:")
        print(f"• Graph databases excel at complex, multi-hop queries")
        print(f"• Social network analysis is natural with graph traversals")
        print(f"• CQL would require complex application logic and multiple queries")
    
    def show_performance_summary(self):
        """Show a summary of when to use each approach."""
        self.print_header("PERFORMANCE & USAGE SUMMARY")
        
        print(f"{Fore.GREEN}When to use JanusGraph (Graph Database):")
        print("• Complex relationship queries and traversals")
        print("• Recommendation engines and collaborative filtering")
        print("• Social network analysis")
        print("• Fraud detection with relationship patterns")
        print("• Multi-hop queries (friend-of-friend, etc.)")
        print("• Exploratory data analysis")
        
        print(f"\n{Fore.GREEN}When to use Direct CQL (ScyllaDB):")
        print("• Simple key-value lookups")
        print("• Time-series data and analytics")
        print("• High-throughput write workloads")
        print("• Known query patterns with optimal data modeling")
        print("• Range queries and pagination")
        print("• When you need predictable, low-latency performance")
        
        print(f"\n{Fore.CYAN}Best Practice - Hybrid Approach:")
        print("• Use both systems for their strengths")
        print("• JanusGraph for complex analytics and relationships")
        print("• Direct CQL for operational queries and high-throughput operations")
        print("• Keep data synchronized between systems")


@click.command()
@click.option('--setup', is_flag=True, help='Setup databases and schemas')
@click.option('--generate', is_flag=True, help='Generate test data')
@click.option('--load-graph', is_flag=True, help='Load data into JanusGraph')
@click.option('--load-cql', is_flag=True, help='Load data into ScyllaDB via CQL')
@click.option('--demo', is_flag=True, help='Run access pattern demonstrations')
@click.option('--all', 'run_all', is_flag=True, help='Run complete demo (setup, generate, load, demo)')
@click.option('--summary', is_flag=True, help='Show performance and usage summary')
def main(setup, generate, load_graph, load_cql, demo, run_all, summary):
    """JanusGraph with ScyllaDB Example Application."""
    
    demo_app = ECommerceDemo()
    
    try:
        if run_all:
            setup = generate = load_graph = load_cql = demo = summary = True
        
        if setup:
            demo_app.setup_databases()
        
        if generate:
            demo_app.generate_test_data()
        
        if load_graph:
            demo_app.load_data_to_graph()
        
        if load_cql:
            demo_app.load_data_to_cql()
        
        if demo:
            demo_app.demonstrate_access_patterns()
        
        if summary:
            demo_app.show_performance_summary()
        
        if not any([setup, generate, load_graph, load_cql, demo, run_all, summary]):
            print("Use --help to see available options or --all to run complete demo")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Demo failed: {e}")
        logger.exception("Demo failed")
    finally:
        # Cleanup connections
        db_manager.disconnect_all()
        print(f"\n{Fore.GREEN}Demo complete. Connections closed.")


if __name__ == "__main__":
    main()