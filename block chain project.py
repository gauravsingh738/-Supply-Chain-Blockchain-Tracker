import hashlib
import json
from time import time
from tabulate import tabulate
from colorama import Fore, init
import os

init(autoreset=True)

USERS_FILE = "users.json"
BLOCKCHAIN_FILE = "blockchain.json"

users = {}
logged_in_user = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

### --- PERSISTENCE HELPERS ---

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_users():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    else:
        users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin"
            },
            "user1": {
                "password": hash_password("user123"),
                "role": "user"
            }
        }
        save_users()

def save_blockchain(chain):
    data = [block.to_dict() for block in chain]
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump(data, f)

def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as f:
            blocks = json.load(f)
        chain = []
        for block_data in blocks:
            block = Block.from_dict(block_data)
            chain.append(block)
        return chain
    return None

### --- USER MANAGEMENT ---

def register():
    print(Fore.CYAN + "\n--- Register User ---")
    username = input("Username: ").strip()
    if username in users:
        print(Fore.RED + "⚠️ User already exists.")
        return
    password = input("Password: ").strip()
    role = input("Role (admin/user): ").strip().lower()
    if role not in ["admin", "user"]:
        print(Fore.RED + "⚠️ Invalid role. Use 'admin' or 'user'.")
        return
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users()
    print(Fore.GREEN + "✅ Registration successful.")

def login():
    global logged_in_user
    print(Fore.CYAN + "\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = users.get(username)
    if not user or user["password"] != hash_password(password):
        print(Fore.RED + "❌ Invalid credentials.")
        return False
    logged_in_user = {
        "username": username,
        "role": user["role"]
    }
    print(Fore.GREEN + f"✅ Welcome, {username} ({user['role']})!")
    return True

def remove_user():
    if logged_in_user["role"] != "admin":
        print(Fore.RED + "Only admins can remove users.")
        return
    username = input("Username to remove: ").strip()
    if username not in users:
        print(Fore.RED + "User not found.")
        return
    if username == logged_in_user["username"]:
        print(Fore.RED + "You can't remove yourself!")
        return
    del users[username]
    save_users()
    print(Fore.YELLOW + "✅ User removed.")

def list_users():
    print(tabulate(
        [[u, d['role']] for u, d in users.items()],
        headers=["Username", "Role"],
        tablefmt="fancy_grid"
    ))

### --- BLOCKCHAIN CORE ---

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0, hash_value=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash_value or self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            index=d["index"],
            timestamp=d["timestamp"],
            data=d["data"],
            previous_hash=d["previous_hash"],
            nonce=d.get("nonce", 0),
            hash_value=d.get("hash")
        )

class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = load_blockchain() or []
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        print(Fore.YELLOW + "⛏️  Creating genesis block...")
        genesis_block = Block(0, time(), {"event": "Genesis Block"}, "0")
        self.chain.append(genesis_block)
        save_blockchain(self.chain)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        last_block = self.get_last_block()
        new_block = Block(index=last_block.index + 1,
                        timestamp=time(),
                        data=data,
                        previous_hash=last_block.hash)
        print(Fore.YELLOW + "⛏️  Mining block...")
        start = time()
        mined_block = self.proof_of_work(new_block)
        end = time()
        self.chain.append(mined_block)
        save_blockchain(self.chain)
        print(Fore.GREEN + f"✅ Block {mined_block.index} mined in {round(end - start, 2)} seconds.")

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        block.hash = computed_hash
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.compute_hash():
                print(Fore.RED + f"❌ Block {curr.index} has been tampered!")
                return False
            if curr.previous_hash != prev.hash:
                print(Fore.RED + f"❌ Block {curr.index} previous hash mismatch!")
                return False
        return True

    def search_events(self, product_id):
        results = []
        for block in self.chain:
            ev = block.data
            if isinstance(ev, dict) and ev.get('Product ID', None) == product_id:
                results.append(block)
        return results

    def filter_events_by_user(self, user):
        results = []
        for block in self.chain:
            ev = block.data
            if isinstance(ev, dict) and (ev.get('Sender') == user or ev.get('Receiver') == user):
                results.append(block)
        return results

### --- SUPPLY CHAIN TRACKER ---

class SupplyChainTracker:
    def __init__(self):
        self.blockchain = Blockchain()

    def add_event(self, sender, receiver, product_id, event_type, info):
        event = {
            'Product ID': product_id,
            'Sender': sender,
            'Receiver': receiver,
            'Event': event_type,
            'Info': info,
            'Timestamp': time_to_str(time())
        }
        self.blockchain.add_block(event)

    def view_chain(self):
        table = []
        for block in self.blockchain.chain:
            table.append([
                block.index,
                time_to_str(block.timestamp),
                block.data if isinstance(block.data,str) else json.dumps(block.data),
                block.previous_hash[:10] + "...",
                block.hash[:10] + "...",
                block.nonce
            ])
        headers = ['Index', 'BlockTS', 'Data', 'Prev Hash', 'Hash', 'Nonce']
        print("\n📦 Blockchain Overview")
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    def validate_chain(self):
        print("\n🔍 Validating Blockchain...")
        valid = self.blockchain.is_chain_valid()
        if valid:
            print(Fore.GREEN + "✅ Blockchain integrity verified.")
        else:
            print(Fore.RED + "❌ Blockchain has been compromised!")

    def search_events(self, product_id):
        blocks = self.blockchain.search_events(product_id)
        if not blocks:
            print(Fore.RED + "No events for Product ID:", product_id)
            return
        table = []
        for block in blocks:
            table.append([
                block.index,
                time_to_str(block.timestamp),
                block.data
            ])
        print(tabulate(table, headers=['Index', 'BlockTS', 'Event'], tablefmt="github"))

    def filter_events_by_user(self, user):
        blocks = self.blockchain.filter_events_by_user(user)
        if not blocks:
            print(Fore.RED + "No events for user:", user)
            return
        table = []
        for block in blocks:
            table.append([
                block.index,
                time_to_str(block.timestamp),
                block.data
            ])
        print(tabulate(table, headers=['Index', 'BlockTS', 'Event'], tablefmt="github"))

def time_to_str(ts):
    from datetime import datetime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

### --- APPLICATION MENU ---

def main_menu(tracker):
    while True:
        print(Fore.CYAN + "\n=== Supply Chain Tracker ===")
        print(Fore.BLUE + "1. Add Supply Chain Event")
        print("2. View Blockchain")
        print("3. Validate Chain")
        print("4. Search by Product ID")
        print("5. Search by User")
        if logged_in_user["role"] == "admin":
            print(Fore.RED + "6. User Management")
        print("0. Logout & Exit")
        choice = input(Fore.CYAN + "Enter choice: ")
        if choice == '1':
            sender = logged_in_user["username"]
            receiver = input("Receiver: ")
            product_id = input("Product ID: ")
            print("Event Types: Dispatched, In Transit, Delivered, Custom")
            event_type = input("Event Type: ")
            info = input("Additional Info: ")
            tracker.add_event(sender, receiver, product_id, event_type, info)
            print(Fore.GREEN + "✅ Event added successfully.")
        elif choice == '2':
            tracker.view_chain()
        elif choice == '3':
            tracker.validate_chain()
        elif choice == '4':
            pid = input("Product ID: ")
            tracker.search_events(pid)
        elif choice == '5':
            uname = input("User: ")
            tracker.filter_events_by_user(uname)
        elif choice == '6' and logged_in_user["role"] == "admin":
            user_management_menu()
        elif choice == '0':
            print(Fore.YELLOW + "Exiting... 👋")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

def user_management_menu():
    while True:
        print(Fore.CYAN + "\n--- Admin - User Management ---")
        print(Fore.BLUE + "1. Register User")
        print("2. Remove User")
        print("3. List Users")
        print("0. Back")
        choice = input("Choice: ")
        if choice == '1':
            register()
        elif choice == '2':
            remove_user()
        elif choice == '3':
            list_users()
        elif choice == '0':
            break
        else:
            print(Fore.RED + "Invalid choice.")

def main():
    load_users()
    global logged_in_user
    print(Fore.CYAN + "Welcome to Supply Chain Blockchain Tracker")
    attempts = 0
    while not logged_in_user:
        print("\n1. Login\n2. Register\n3. Exit")
        c = input("Choice: ")
        if c == '1':
            if login():
                break
            attempts += 1
            if attempts > 2:
                print(Fore.YELLOW + "Too many failed attempts. Exiting.")
                return
        elif c == '2':
            register()
        elif c == '3':
            return
        else:
            print("Invalid choice.")

    tracker = SupplyChainTracker()
    main_menu(tracker)

if __name__ == "__main__":
    main()

