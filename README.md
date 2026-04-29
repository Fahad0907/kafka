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
