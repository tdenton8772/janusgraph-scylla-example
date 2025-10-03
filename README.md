# JanusGraph with ScyllaDB Example

A comprehensive example application demonstrating the differences between graph-based and traditional CQL-based access patterns using JanusGraph with ScyllaDB as the backend storage.

## 🎯 Overview

This project showcases how the same e-commerce data can be accessed through two fundamentally different approaches:

- **Graph Database (JanusGraph)**: Complex relationship traversals, recommendations, social network analysis
- **Direct CQL (ScyllaDB)**: Shard-aware optimized queries, high-throughput operations, known access patterns

⚠️ **Important Note**: This demo currently uses **data duplication** across two separate keyspaces to demonstrate both approaches. While educational, this undermines the core value proposition of a single data store serving multiple access patterns. See the [Architecture Concerns](#-architecture-concerns) section for details and potential solutions.

Using an e-commerce domain with users, products, orders, and reviews, this demo illustrates the trade-offs between different database access patterns.

## 🏗️ Current Architecture

### Data Storage Layout

This demo uses **two separate keyspaces** on the same ScyllaDB cluster:

```
                     ┌─────────────────────────────────────┐
                     │           ScyllaDB CLUSTER          │
                     │                                     │
┌────────────────────┼─────────────────────────────────────┼─────────────────────┐
│                    │                                     │                     │
│  ┌─────────────────▼─────────────────────────────────────▼──────────────────┐  │
│  │                    JANUSGRAPH KEYSPACE                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │ edgestore   │  │ graphindex  │  │ systemlog   │  │janusgraph   │    │  │
│  │  │             │  │             │  │             │  │   _ids      │    │  │
│  │  │ Graph data  │  │ Indexes     │  │ Metadata    │  │             │    │  │
│  │  │ (vertices   │  │ (composite, │  │ (schemas,   │  │ ID          │    │  │
│  │  │  & edges)   │  │  vertex-    │  │  configs)   │  │ management  │    │  │
│  │  │             │  │  centric)   │  │             │  │             │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    ECOMMERCE KEYSPACE                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │   users     │  │  products   │  │   orders    │  │ order_items │    │  │
│  │  │             │  │             │  │             │  │             │    │  │
│  │  │ Application │  │ Catalog     │  │ Transaction │  │ Order line  │    │  │
│  │  │ users       │  │ data        │  │ history     │  │ items       │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  │                                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │  │
│  │  │  reviews    │  │ user_orders │  │ products_by │                     │  │
│  │  │             │  │             │  │  _category  │                     │  │
│  │  │ Product     │  │ Denormalized│  │             │                     │  │
│  │  │ reviews     │  │ for fast    │  │ Optimized   │                     │  │
│  │  │             │  │ user lookup │  │ browsing    │                     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                     │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ▲                            ▲
                              │                            │
                    ┌─────────┴────────┐        ┌────────┴────────┐
                    │   JanusGraph     │        │  Direct CQL     │
                    │   (Gremlin API)  │        │  (Python App)   │
                    │                  │        │                 │
                    │ • Graph queries  │        │ • Table queries │
                    │ • Traversals     │        │ • Key lookups   │
                    │ • Complex paths  │        │ • Range scans   │
                    │ • Relationships  │        │ • Aggregations  │
                    └──────────────────┘        └─────────────────┘
```

### Data Flow

1. **Same source data** → Generated once by Python application
2. **Loaded twice** → Into both `janusgraph` and `ecommerce` keyspaces
3. **Two access paths** → JanusGraph API vs Direct CQL
4. **Same physical storage** → All data stored on ScyllaDB cluster

## ⚠️ Architecture Concerns

### The Data Duplication Problem

The current implementation has a **significant architectural flaw**: it duplicates the entire dataset across two keyspaces. This undermines the core value proposition of using a single data store for multiple access patterns.

#### Issues with Current Approach:

1. **Data Inconsistency Risk**
   - Same business entity exists in multiple places
   - Updates must be synchronized across keyspaces
   - Risk of data drift and inconsistencies

2. **Storage Overhead**
   - 2x storage requirements (same data stored twice)
   - Increased memory usage and disk space
   - Higher infrastructure costs

3. **Operational Complexity**
   - Two separate data loading processes
   - Complex synchronization requirements
   - Increased backup and maintenance overhead

4. **Defeats Single Source of Truth**
   - The fundamental benefit of unified storage is lost
   - Creates "distributed data" problems within a single cluster

### Better Architectural Approaches

#### Option 1: JanusGraph Only (Recommended)
```
┌───────────────────────────────────────────────────┐
│                ScyllaDB Cluster                           │
│                                                           │
│    ┌───────────────── JANUSGRAPH KEYSPACE ─────────────────┐    │
│    │                                                     │    │
│    │     📊 Single source of truth for all data        │    │
│    │     🔄 Graph structure enables both access patterns  │    │
│    │     🚀 JanusGraph indexes optimize CQL-like queries │    │
│    │                                                     │    │
│    └───────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────┘
                ┌───────────┐ ┌───────────────┐
                │ Gremlin   │ │ Direct CQL*   │
                │ Traversal │ │ (via indexes) │
                └───────────┘ └───────────────┘

*Use JanusGraph’s composite indexes for CQL-like performance
```

**Advantages:**
- ✅ Single source of truth
- ✅ No data duplication
- ✅ JanusGraph indexes can optimize simple lookups
- ✅ Complex relationships available when needed
- ✅ Simplified operations and maintenance

**Implementation:**
- Create comprehensive JanusGraph indexes for common lookup patterns
- Use Gremlin queries that leverage indexes for simple operations
- Leverage graph traversals for complex analytics

#### Option 2: ScyllaDB Only
```
┌───────────────────────────────────────────────────┐
│                ScyllaDB Cluster                           │
│                                                           │
│    ┌───────────────── ECOMMERCE KEYSPACE ─────────────────┐    │
│    │                                                     │    │
│    │     📊 Optimized tables for all access patterns      │    │
│    │     🔄 Denormalized views for relationships        │    │
│    │     🚀 Application-level graph logic              │    │
│    │                                                     │    │
│    └───────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────┘
                ┌───────────────────────────────┐
                │ Application with graph logic │
                │ Multiple CQL queries + joins  │
                └───────────────────────────────┘
```

**Advantages:**
- ✅ Predictable performance for known patterns
- ✅ Lower operational complexity
- ✅ Maximum ScyllaDB optimization

**Disadvantages:**
- ❌ Complex application logic for relationships
- ❌ Difficult to handle unknown query patterns
- ❌ Performance degradation for multi-hop queries

### Current Demo Value

Despite the duplication issue, this demo **still provides educational value** by:

- ✅ **Comparing query approaches**: Shows the difference between graph traversal and tabular access
- ✅ **Performance benchmarking**: Demonstrates the performance characteristics of each approach
- ✅ **Access pattern analysis**: Highlights when to choose which approach
- ✅ **Implementation examples**: Provides working code for both patterns

**Bottom Line**: This is an excellent **learning and comparison tool**, but should **not be used as a production architecture pattern**.

## ❓ Can CQL Access JanusGraph Data?

**TL;DR**: Technically yes, but practically **NO** for normal use cases.

### What We Discovered

JanusGraph stores all data in ScyllaDB using a **binary blob format**:

```sql
-- JanusGraph table structure
CREATE TABLE edgestore (
    key blob,           -- Binary-encoded entity ID
    column1 blob,       -- Binary-encoded property/relationship type
    value blob,         -- Binary-encoded property value + metadata
    PRIMARY KEY (key, column1)
);
```

### Investigation Results

✅ **Raw data IS accessible via CQL**:
```bash
# We found actual emails, usernames, and text in the binary data:
• walkerjessica@example.co
• product descriptions and review comments
• user addresses and names
```

❌ **BUT it's NOT practically usable**:
- Data mixed with binary serialization artifacts
- No way to query by business logic ("find user by email")
- Requires understanding JanusGraph's internal binary format
- Full table scans required - no indexes on readable content
- Would break with JanusGraph version updates

### Binary Format Example

```python
# What you see in CQL:
Row(key=b'\xa0\x00\x00\x00\x00\x00\xc0\x00', 
    column1=b'P\xa0', 
    value=b'\xa0walkerjessica@example.co\xb8zL\x94')
    
# The email is there, but buried in binary metadata!
```

### Implications for Architecture

This confirms that **Option 1 (JanusGraph Only)** from our architectural recommendations is **theoretically valid**:

✅ **Single source of truth IS possible**:
- All business data is stored once in JanusGraph's keyspace
- Simple lookups could be done via well-designed JanusGraph indexes
- Complex relationships handled by graph traversals
- No data duplication

❌ **But requires careful index design**:
- Must create composite indexes for all CQL-like query patterns
- Performance depends on JanusGraph's index implementation
- More complex than separate CQL tables

### Practical Recommendation

For production systems:
1. **Choose one primary data store** (either JanusGraph OR ScyllaDB)
2. **Design comprehensive indexes** for your chosen store
3. **Don't try to access JanusGraph data via raw CQL**
4. **Use proper APIs** (Gremlin for JanusGraph, CQL for ScyllaDB)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- curl (for health checks)

### Setup & Run

```bash
# 1. Clone and navigate to project
cd ~/Development/janusgraph-scylla-example

# 2. Setup environment
./scripts/setup.sh setup

# 3. Start services  
./scripts/setup.sh start

# 4. Run the demo
./scripts/setup.sh demo
```

That's it! The demo will generate test data and demonstrate different access patterns.

## 📁 Project Structure

```
janusgraph-scylla-example/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.template                      # Environment configuration template
│
├── docker/                           # Docker configuration
│   └── docker-compose.yml            # JanusGraph + ScyllaDB services
│
├── config/                           # Database configurations
│   └── janusgraph.properties         # JanusGraph configuration
│
├── python/                           # Python application
│   ├── ecommerce_demo.py             # Main demo application
│   └── ecommerce/                    # Application packages
│       ├── config.py                 # Settings and configuration
│       ├── models.py                 # Data models (Pydantic)
│       ├── services/                 
│       │   ├── database.py           # Database connections
│       │   └── data_generator.py     # Test data generation
│       └── queries/
│           ├── graph_queries.py      # JanusGraph/Gremlin queries
│           └── cql_queries.py        # Direct ScyllaDB/CQL queries
│
├── scripts/                          # Utility scripts
│   └── setup.sh                     # Setup and management script
│
└── src/main/resources/               # Schema definitions
    └── schema.cql                    # CQL table schemas
```

## 🗄️ Data Schema

### E-commerce Domain

The demo uses a realistic e-commerce scenario with:

- **Users**: Customers with profiles and preferences
- **Products**: Catalog items with categories, brands, and prices
- **Orders**: Purchase transactions with items and status
- **Reviews**: Product reviews with ratings and comments

### Graph Schema (JanusGraph)

```
[User] ─placed_order→ [Order]
[User] ─wrote_review→ [Review] ←has_review─ [Product]
```

### CQL Schema (ScyllaDB)

Optimized tables for specific access patterns:

```cql
-- Main entities
users (user_id, username, email, ...)
products (product_id, name, category, brand, ...)
orders (order_id, user_id, order_date, ...)
reviews (product_id, review_id, user_id, rating, ...)

-- Optimized lookup tables
user_orders (user_id, order_date, order_id) 
products_by_category (category, created_date, product_id)
user_reviews (user_id, review_date, review_id)
```

## 🔄 Access Pattern Comparisons

### 1. Simple Lookups

**Use Case**: Get user's order history

**Graph (JanusGraph)**:
```python
# Single traversal
g.V(user_id).out('placed_order').valueMap().limit(10)
```

**CQL (ScyllaDB)**:
```sql
-- Optimized with partitioning
SELECT * FROM user_orders WHERE user_id = ? LIMIT 10
```

**Winner**: CQL - Faster for simple key-based lookups

### 2. Product Recommendations

**Use Case**: Find products similar users have bought

**Graph (JanusGraph)**:
```python
# Complex multi-hop traversal
g.V(user_id).out('placed_order')      # User's orders  
  .in_('placed_order')                # Other users with same orders
  .where(neq(V(user_id)))            # Exclude original user
  .out('placed_order')               # Their other orders
  .dedup().limit(5)                  # Unique recommendations
```

**CQL (ScyllaDB)**:
```python
# Requires multiple queries + application logic:
# 1. Get user's orders
# 2. For each product, find other users
# 3. Get their other orders  
# 4. Aggregate and rank results
```

**Winner**: Graph - Natural for relationship-based queries

### 3. Category Browsing

**Use Case**: Browse products by category

**Graph (JanusGraph)**:
```python
# Filter by property
g.V().hasLabel('product').has('category', category_name)
```

**CQL (ScyllaDB)**:
```sql
-- Dedicated optimized table
SELECT * FROM products_by_category WHERE category = ?
```

**Winner**: CQL - Purpose-built for this access pattern

### 4. Social Network Analysis

**Use Case**: Find users connected through purchases

**Graph (JanusGraph)**:
```python
# Multi-hop relationship analysis
g.V(user_id).out('placed_order')
  .in_('placed_order')              # Connected users
  .dedup().count()                  # Connection count
```

**CQL (ScyllaDB)**:
```python
# Complex application-level joins required
# Multiple queries + significant processing
```

**Winner**: Graph - Excels at relationship analysis

## 🚀 ScyllaDB Driver Advantages

This project uses the **ScyllaDB Python Driver** (not the generic Cassandra driver) for several key benefits:

### Shard-Aware Routing
```python
# ScyllaDB driver automatically routes queries to the correct shard
# No need for manual partition key calculation
result = session.execute(prepared_stmt, [user_id, limit])
```

### Performance Optimizations
- **Prepared Statements**: Cached and reused for better performance
- **LZ4 Compression**: Reduced network overhead
- **Protocol v4**: Latest CQL protocol features
- **Connection Pooling**: Optimized for ScyllaDB's architecture

### Why Not Cassandra Driver?
```python
# ❌ Generic Cassandra driver
from cassandra.cluster import Cluster  # Not shard-aware

# ✅ ScyllaDB-optimized driver  
from scylla.cluster import Cluster     # Shard-aware routing
```

**Performance Impact**: 2-10x better performance in many scenarios due to:
- Reduced cross-shard queries
- Better connection management
- ScyllaDB-specific optimizations

## 🎮 Demo Features

The demo application includes:

### Interactive Demonstrations

1. **User Order History** - Compare simple lookup performance
2. **Product Reviews** - Show partitioned vs. traversal access
3. **Product Recommendations** - Highlight graph advantages
4. **Category Browsing** - Demonstrate CQL optimization
5. **Complex Analysis** - Social networks and trends

### Performance Comparisons

Real-time timing comparisons showing:
- Query execution times
- Code complexity differences
- Scalability considerations

### Data Generation

- Realistic fake data using Python Faker
- Configurable dataset sizes
- Proper relationship modeling

## ⚙️ Configuration

### Environment Variables

Key settings in `.env` file:

```bash
# ScyllaDB Connection (for cloud deployment)
SCYLLA_HOST=your-cluster.scylladb.com
SCYLLA_PORT=9042
SCYLLA_USERNAME=your_username
SCYLLA_PASSWORD=your_password
SCYLLA_SSL_ENABLED=true

# Local Development (default)
SCYLLA_HOST=localhost
SCYLLA_PORT=9042
SCYLLA_SSL_ENABLED=false

# Data Generation
NUM_USERS=100
NUM_PRODUCTS=200
MAX_ORDERS_PER_USER=5
MAX_REVIEWS_PER_PRODUCT=10
```

### Cloud ScyllaDB Setup

To use with a cloud ScyllaDB cluster:

1. Update `.env` with your cluster details
2. Add SSL certificates if required
3. Configure authentication credentials
4. Update `docker-compose.yml` environment variables

## 🎯 When to Use What

### Choose JanusGraph (Graph Database) for:

✅ **Complex Relationship Queries**
- Friend-of-friend recommendations
- Fraud detection through transaction patterns
- Supply chain analysis

✅ **Exploratory Data Analysis**
- Unknown query patterns
- Discovering hidden relationships
- Interactive graph exploration

✅ **Multi-hop Traversals**
- Social network analysis
- Recommendation engines
- Path finding algorithms

### Choose Direct CQL (ScyllaDB) for:

✅ **High-Throughput Operations**
- Real-time analytics
- IoT data ingestion
- Time-series data

✅ **Known Query Patterns**
- Optimized table design
- Predictable performance
- Simple key-value lookups

✅ **Low-Latency Requirements**
- User-facing applications
- Real-time dashboards
- Operational queries

### ⚠️ About the "Hybrid Approach"

**Current Implementation Issues:**
The demo shows a "hybrid approach" but with **major architectural problems**:
- **Data Duplication**: Same data stored in both `janusgraph` and `ecommerce` keyspaces
- **Synchronization Complexity**: Updates must be applied to both stores
- **Storage Overhead**: 2x storage requirements
- **Operational Burden**: Two separate maintenance processes

**Better Production Approaches:**
1. **Choose One Primary Store** - Use JanusGraph OR ScyllaDB as the single source of truth
2. **Event-Driven Architecture** - If you must use both, implement proper CDC/event streaming
3. **Microservices Pattern** - Different services own different data domains

**This Demo's Value:** Educational comparison only - not a production pattern to follow

## 🛠️ Management Commands

```bash
# Setup and start everything
./scripts/setup.sh setup && ./scripts/setup.sh start

# Individual operations
./scripts/setup.sh start       # Start Docker services
./scripts/setup.sh stop        # Stop Docker services  
./scripts/setup.sh status      # Check service status
./scripts/setup.sh demo        # Run demo application
./scripts/setup.sh clean       # Clean up resources

# Python demo options
python3 python/ecommerce_demo.py --help
python3 python/ecommerce_demo.py --all          # Full demo
python3 python/ecommerce_demo.py --setup        # Setup only
python3 python/ecommerce_demo.py --generate     # Generate data
python3 python/ecommerce_demo.py --demo         # Run demos
```

## 📊 Performance Considerations

### Graph Database (JanusGraph)
- **Pros**: Excellent for complex traversals, relationship analysis
- **Cons**: Higher memory usage, more complex setup
- **Best for**: Analytics, recommendations, exploratory queries

### Direct CQL (ScyllaDB)
- **Pros**: Predictable performance, high throughput, simple model
- **Cons**: Requires knowing query patterns upfront
- **Best for**: Operational workloads, known access patterns

## 🔧 Troubleshooting

### Common Issues

**JanusGraph won't start**:
```bash
# Check Docker logs
docker-compose -f docker/docker-compose.yml logs janusgraph

# Verify ScyllaDB connection
docker-compose -f docker/docker-compose.yml logs
```

**Connection errors**:
```bash
# Verify services are running
./scripts/setup.sh status

# Check network connectivity
curl http://localhost:8182
```

**Data loading fails**:
```bash
# Ensure databases are set up
python3 python/ecommerce_demo.py --setup

# Check keyspace creation
cqlsh localhost 9042 -e "DESCRIBE KEYSPACES"
```

### Docker Issues

```bash
# Clean restart
./scripts/setup.sh clean
./scripts/setup.sh start

# Check Docker resources
docker system df
docker system prune
```

## 📚 Learn More

### JanusGraph Resources
- [JanusGraph Documentation](https://docs.janusgraph.org/)
- [Gremlin Query Language](https://tinkerpop.apache.org/docs/current/reference/#traversal)
- [Graph Database Concepts](https://docs.janusgraph.org/basics/schema/)

### ScyllaDB Resources
- [ScyllaDB Documentation](https://docs.scylladb.com/)
- [CQL Reference](https://docs.scylladb.com/stable/cql/)
- [Data Modeling Guide](https://docs.scylladb.com/stable/data-modeling/)

### Graph vs. Relational
- [When to Use Graph Databases](https://neo4j.com/developer/graph-database/)
- [Graph Database Use Cases](https://docs.janusgraph.org/getting-started/use-cases/)

## 🤝 Contributing

This is a demonstration project. Suggested improvements:

1. Add more complex graph algorithms
2. Implement real-time data synchronization
3. Add performance benchmarking suite
4. Create visualization components
5. Add more realistic data patterns

## 📄 License

This example project is provided as-is for educational and demonstration purposes.

---

**Happy Graph Querying!** 🎉

For questions or issues, please check the troubleshooting section or review the Docker logs for detailed error information.# janusgraph-scylla-example
