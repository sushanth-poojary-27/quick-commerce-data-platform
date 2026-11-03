from src.db import get_db_connection
from  faker import Faker

fake = Faker('en_IN')  # Use Indian locale for realistic data

Faker.seed(42)

def seed_stores():
    mumbai_stores = [
        (
            "Bandra West Hub",
            "Shop 4, Hill Road, Bandra West",
            "Mumbai",
            "400050",
        ),
        (
            "Andheri East Warehouse",
            "Unit 12, MIDC Central Road, Andheri East",
            "Mumbai",
            "400093",
        ),
        (
            "Lower Parel Point",
            "Phoenix Mills Compound, SB Marg, Lower Parel",
            "Mumbai",
            "400013",
        ),
        (
            "Powai Distribution Center",
            "Building 3, Hiranandani Gardens, Powai",
            "Mumbai",
            "400076",
        ),
        (
            "Malad West Hub",
            "Link Road Industrial Estate, Malad West",
            "Mumbai",
            "400064",
        ),
    ] 

    insert_query = """
        INSERT INTO stores (store_name, address, city, zip_code)
        VALUES (%s, %s, %s, %s);
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.executemany(insert_query, mumbai_stores)
        conn.commit()
        print(f"Stores seeded successfully! {len(mumbai_stores)} records inserted.")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding stores: {e}")
    finally:
        cur.close()
        conn.close()


def seed_products():
    products = [
    # Dairy & Breakfast
    (
        "Amul Taaza Homogenised Toned Milk 1L",
        "Pasteurised toned milk with 3.0% fat and 8.5% SNF",
        54.00,
        "Dairy & Breakfast",
        150,
    ),
    (
        "Amul Salted Butter 500g",
        "Rich, creamy butter made from fresh cream",
        275.00,
        "Dairy & Breakfast",
        80,
    ),
    (
        "Kellogg's Real Almond & Honey Corn Flakes 300g",
        "Crispy toasted golden corn flakes with real honey and sliced almonds",
        195.00,
        "Dairy & Breakfast",
        60,
    ),
    # Snacks & Munchies
    (
        "Lay's India's Magic Masala Potato Chips 50g",
        "Spicy ridged potato chips seasoned with Indian spices",
        20.00,
        "Snacks & Munchies",
        200,
    ),
    (
        "Haldiram's Nagpur Bhujia Sev 400g",
        "Crispy and spicy tepary bean and gram flour noodle snack",
        115.00,
        "Snacks & Munchies",
        90,
    ),
    (
        "Britannia Bourbon Chocolate Cream Biscuits 150g",
        "Rich chocolate cream sandwiched between crunchy sugar-sprinkled biscuits",
        35.00,
        "Snacks & Munchies",
        120,
    ),
    # Beverages
    (
        "Coca-Cola Original Taste 750ml",
        "Refreshing and crisp carbonated soft drink",
        40.00,
        "Beverages",
        110,
    ),
    (
        "Tata Tea Gold 500g",
        "Black tea blended with gently rolled aromatic long leaves",
        310.00,
        "Beverages",
        70,
    ),
    (
        "Paper Boat Aamras Mango Fruit Juice 250ml",
        "Authentic sweet mango pulp beverage with no preservatives",
        35.00,
        "Beverages",
        85,
    ),
    # Instant Food
    (
        "Maggi 2-Minute Masala Noodles 280g",
        "Pack of 4 instant noodles with signature tastemaker masala",
        56.00,
        "Instant Food",
        180,
    ),
    (
        "Knorr Sweet Corn Veg Instant Soup 43g",
        "Creamy sweet corn vegetable soup mix ready in minutes",
        35.00,
        "Instant Food",
        95,
    ),
    (
        "Yippee Magic Masala Noodles 240g",
        "Non-sticky round block masala instant noodles",
        48.00,
        "Instant Food",
        140,
    ),
]
    insert_product_query = """
    INSERT INTO products (product_name, description, price, category, stock_quantity)
    VALUES (%s, %s, %s, %s, %s);
"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.executemany(insert_product_query, products)
        conn.commit()
        print(f"Products seeded successfully! {len(products)} records inserted.")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding products: {e}")
    finally:
        cur.close()
        conn.close()

def seed_customers(num_customers=50):
    customers = [
        
        (
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number(),
            fake.address().replace("\n", ", "),
        )
        for _ in range(num_customers)
    ]
    insert_customer_query = """
    INSERT INTO customers (first_name, last_name, email, phone_number, address)
    VALUES (%s, %s, %s, %s, %s);
"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.executemany(insert_customer_query, customers)
        conn.commit()
        print(f"Customers seeded successfully! {len(customers)} records inserted.")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding customers: {e}")
    finally:
        cur.close()
        conn.close()

def seed_orders(num_orders=100):
    conn = None
    cur = None

    try:
       
        conn = get_db_connection()
        cur = conn.cursor()
 
        cur.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT store_id FROM stores;")
        store_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT product_id, price FROM products;")
        products = cur.fetchall()

        print(f"Loaded {len(customer_ids)} customers, {len(store_ids)} stores, {len(products)} products.")

    except Exception as e:
        print(f"Error fetching reference data: {e}")
 
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    #seed_stores()
    #seed_products()
    #seed_customers()
    seed_orders()