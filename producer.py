from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:29092", 
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all", 
    retries=5, 
    enable_idempotence=True 
)

for i in range(10):
    data = {"order_id": i, "status": "created"}
    
    # send with key (controls partition)
    producer.send(
        "orders",
        key=str(i % 2).encode("utf-8"),  # 2 keys → 2 partitions behavior
        value=data
    )
    
    print(f"Sent: {data}")
    time.sleep(1)

producer.flush()
producer.close()