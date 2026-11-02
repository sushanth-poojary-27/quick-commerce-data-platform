from src.db import get_db_connection


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


if __name__ == "__main__":
    seed_stores()