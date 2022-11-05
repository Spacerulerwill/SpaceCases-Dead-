#find ranking of user inventory value
import time
import random

user_inventory_values = [random.randint(0, 100) for i in range(10000000)]

user_inventory_value = 20
less_than = 0
start = time.time()
for item in user_inventory_values:
    if item < user_inventory_value:
        less_than += 1
end = time.time()
print(end-start)
print(len(user_inventory_values) - less_than)