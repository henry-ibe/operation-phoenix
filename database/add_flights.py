"""
Add sample flights to the database
"""
import psycopg2
from datetime import datetime, timedelta
import random

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="phoenix_air",
    user="phoenix_user",
    password="phoenix_dev_password"
)
cur = conn.cursor()

# Airport pairs (routes)
routes = [
    ('JFK', 'LAX'),
    ('LAX', 'JFK'),
    ('JFK', 'ORD'),
    ('ORD', 'JFK'),
    ('JFK', 'ATL'),
    ('ATL', 'JFK'),
    ('LAX', 'SFO'),
    ('SFO', 'LAX'),
    ('ORD', 'SFO'),
    ('SFO', 'ORD'),
    ('ATL', 'LAX'),
    ('LAX', 'ATL'),
]

# Flight times (departure hours)
departure_hours = [6, 8, 10, 12, 14, 16, 18, 20]

# Generate flights for next 14 days
print("Adding flights to database...")
flight_count = 0

for day_offset in range(14):  # Next 2 weeks
    date = datetime.now() + timedelta(days=day_offset)
    
    for origin, destination in routes:
        for hour in random.sample(departure_hours, 3):  # 3 flights per route per day
            
            # Create departure time
            departure = date.replace(hour=hour, minute=random.choice([0, 15, 30, 45]))
            
            # Calculate arrival (rough estimate based on route)
            if abs(ord(origin[0]) - ord(destination[0])) > 10:  # Cross-country
                flight_duration = timedelta(hours=5, minutes=random.randint(0, 45))
            else:  # Shorter flight
                flight_duration = timedelta(hours=2, minutes=random.randint(15, 45))
            
            arrival = departure + flight_duration
            
            # Generate flight number
            flight_number = f"PA{random.randint(100, 999)}"
            
            # Random pricing
            price_economy = round(random.uniform(150, 450), 2)
            price_business = round(price_economy * 2.5, 2)
            price_first = round(price_economy * 4, 2)
            
            # Random aircraft (1 or 2)
            aircraft_id = random.choice([1, 2])
            
            # Seat availability (based on aircraft)
            if aircraft_id == 1:  # Boeing 737
                avail_economy = random.randint(100, 150)
                avail_business = random.randint(10, 20)
                avail_first = random.randint(2, 5)
            else:  # Airbus A320
                avail_economy = random.randint(110, 156)
                avail_business = random.randint(12, 20)
                avail_first = random.randint(1, 4)
            
            # Random gate
            gate = f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 30)}"
            
            # Insert flight
            cur.execute("""
                INSERT INTO flights (
                    flight_number, origin_airport, destination_airport, aircraft_id,
                    scheduled_departure, scheduled_arrival, status, gate,
                    price_economy, price_business, price_first,
                    available_economy, available_business, available_first
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                flight_number, origin, destination, aircraft_id,
                departure, arrival, 'scheduled', gate,
                price_economy, price_business, price_first,
                avail_economy, avail_business, avail_first
            ))
            
            flight_count += 1

# Commit and close
conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully added {flight_count} flights!")
print(f"   Routes: {len(routes)}")
print(f"   Days: 14")
print(f"   Flights per route per day: ~3")
