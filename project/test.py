import hashlib
import uuid
from datetime import datetime

# Test hashlib
data = "Blockchain Certificate"
hash_result = hashlib.sha256(data.encode()).hexdigest()
print(f"SHA-256 Hash: {hash_result}")

# Test uuid
unique_id = uuid.uuid4()
print(f"Generated UUID: {unique_id}")

# Test datetime
current_time = datetime.now()
print(f"Current Time: {current_time}")
