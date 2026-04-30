# Kafka Topic & Partition Details

## Create Topic

```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

**Output:**

```
Created topic test-topic.
```

---

## Describe Topic

```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --describe \
  --topic test-topic \
  --bootstrap-server localhost:9092
```

---

## 🔑 1. Leader

**Leader = the broker that handles all reads & writes for that partition**

**Example:**

```
Partition: 0  Leader: 1
```

Broker `1` is responsible for:

* Receiving messages (producer writes)
* Serving consumers (reads)

**Important:**

* There is only **ONE leader per partition**
* Producers & consumers always talk to the leader

---

## 🔁 2. Replicas

**Replicas = copies of that partition on brokers**

**Example:**

```
Replicas: 1
```

* Means this partition exists on broker `1`

If replication factor = 3:

```
Replicas: 1,2,3
```

**Purpose:**

* Fault tolerance (backup copies)

---

## ✅ 3. ISR (In-Sync Replicas)

**ISR = replicas that are fully up-to-date with the leader**

**Example:**

```
Isr: 1
```

* Broker `1` is in sync with leader (good ✅)

If multiple brokers:

```
Replicas: 1,2,3
Isr: 1,2
```

* Broker `3` is out of sync ❌

**Why ISR matters:**

* Kafka only considers ISR replicas as safe
* Writes are acknowledged based on ISR (depending on config)

---

## ⚠️ 4. ELR (Eligible Leader Replicas)

**ELR = replicas that can become leader if current leader fails**

**Example:**

```
Elr:
```

(empty)

**Meaning:**

* Kafka didn’t list any special eligible replicas
* Usually same as ISR unless advanced configs are used

---

## 🧾 5. LastKnownElr

**Stores last known eligible leader replicas**

**Example:**

```
LastKnownElr:
```

(empty → normal for simple setups)

---

## 🧠 Putting it together (your case)

```
Partition: 0
Leader: 1
Replicas: 1
Isr: 1
```

**Interpretation:**

* Only 1 broker exists (single-node setup)
* No replication (replication factor = 1)
* Everything is healthy ✅

---

## 🔥 Real-world scenario (multi-broker)

```
Partition: 0
Leader: 2
Replicas: 1,2,3
Isr: 2,3
```

**Meaning:**

* Broker 2 = leader
* Broker 1 = lagging (not in ISR)
* Broker 3 = healthy replica

---

## ⚡ Quick intuition

| Term     | Meaning                    |
| -------- | -------------------------- |
| Leader   | Main node handling traffic |
| Replicas | Copies of data             |
| ISR      | Healthy, synced replicas   |
| ELR      | Candidates for next leader |

---

## 🧠 Interview-level insight

* Kafka ensures durability using **replication + ISR**
* If leader fails → Kafka elects new leader from ISR
* If ISR shrinks → risk of data loss increases

# Kafka Core Concepts: Producer, Partition, Offset, Consumer & Consumer Group

This document explains how the main components of Kafka are connected and work together.

---

## 🧠 Big Picture

👉 **Producer → Partition → Offset → Consumer → Consumer Group**

---

## 🔄 Message Flow (Step-by-Step)

### 1. Producer sends a message

```python
producer.send("orders", b"order_created")
```

* Producer sends data to a **topic**
* Example topic: `orders`

---

### 2. Kafka selects a partition

If topic has multiple partitions:

```
orders topic
 ├── Partition 0
 ├── Partition 1
 └── Partition 2
```

Kafka decides:

* With key → same partition (based on hash)
* Without key → round-robin

---

### 3. Message is stored in partition

Each partition is like a log:

```
Partition 1
-------------
Offset 0 → old message
Offset 1 → old message
Offset 2 → order_created
```

---

### 4. Offset is assigned

* Offset = position of message inside partition
* Always increasing (0,1,2,3...)

```
Offset = 2
```

---

## 🔑 Core Concepts

---

### 🧑‍💻 Producer

* Sends messages to Kafka topics
* Can decide partition (using key)
* Controls reliability (acks, retries)

---

### 📦 Partition

* A topic is divided into partitions
* Each partition stores messages
* Enables parallel processing

---

### 🔢 Offset

* Unique ID per message inside a partition
* Used by consumers to track progress

Example:

```
Partition 0 → offsets: 0,1,2
Partition 1 → offsets: 0,1,2
```

⚠️ Offset is **not global**, only per partition

---

### 📥 Consumer

* Reads messages from partitions
* Tracks offset to know where to continue

Example:

```
Consumer reads up to offset 10
Next read starts from offset 11
```

---

### 👥 Consumer Group

* A group of consumers working together
* Share partitions among themselves

---

## 📊 Consumer Group Behavior

### Case 1: Equal consumers and partitions

```
Partitions: 3
Consumers: 3
```

```
Consumer A → Partition 0
Consumer B → Partition 1
Consumer C → Partition 2
```

---

### Case 2: Fewer consumers

```
Partitions: 3
Consumers: 2
```

```
Consumer A → Partition 0,1
Consumer B → Partition 2
```

---

### Case 3: More consumers

```
Partitions: 2
Consumers: 3
```

```
Consumer A → Partition 0
Consumer B → Partition 1
Consumer C → idle
```

---

## 🔁 Offset in Consumer Groups

Each group tracks its own offsets:

```
Group A → offset 100
Group B → offset 50
```

👉 Different applications can read the same topic independently

---

## 🔗 How Everything Connects

```
Producer
   ↓
Topic
   ↓
Partition (chosen by Kafka)
   ↓
Message stored with Offset
   ↓
Consumer reads using Offset
   ↓
Consumer Group manages multiple consumers
```

---

## 🎯 Key Rules

* 1 partition = 1 consumer (per group)
* Ordering is guaranteed **within a partition only**
* Offsets are per partition
* Consumer groups enable scaling

---

## 🔥 Real Example

```
Producer → sends "order_created"

Kafka:
  Partition 0 → Offset 0
  Partition 1 → Offset 0
  Partition 2 → Offset 0

Consumer Group:
  Consumer A → Partition 0
  Consumer B → Partition 1
  Consumer C → Partition 2
```

---

## 🧠 Final Summary

* Producer sends messages
* Kafka stores them in partitions
* Each message gets an offset
* Consumers read messages using offsets
* Consumer groups distribute work across consumers

---

## 💥 Interview One-Liner

> A Kafka producer sends messages to a topic, Kafka assigns them to partitions where each message gets an offset, and consumers in a consumer group read those messages in parallel by dividing partitions among themselves.

