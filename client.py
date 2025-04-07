# client.py
import requests
import sys
import json

API_URL = "http://127.0.0.1:5000"

def add_memory():
    print("\n--- Add Memory ---")
    content = input("Enter memory content: ").strip()
    if not content:
        print("Content cannot be empty.")
        return

    user_id = input("Enter user ID (optional): ").strip() or None

    metadata_input = input("Enter metadata as JSON (optional, e.g., {\"category\": \"hobbies\"}): ").strip()
    if metadata_input:
        try:
            metadata = json.loads(metadata_input)
        except json.JSONDecodeError:
            print("Invalid JSON format for metadata.")
            return
    else:
        metadata = None

    payload = {
        "content": content,
        "user_id": user_id,
        "metadata": metadata
    }

    try:
        response = requests.post(f"{API_URL}/memories/add", json=payload)
        if response.status_code == 201:
            data = response.json()
            print(f"Memory added successfully! Memory ID: {data['memory_id']}")
        else:
            print(f"Failed to add memory. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def update_memory():
    print("\n--- Update Memory ---")
    memory_id = input("Enter Memory ID to update: ").strip()
    if not memory_id:
        print("Memory ID cannot be empty.")
        return

    new_content = input("Enter new content: ").strip()
    if not new_content:
        print("New content cannot be empty.")
        return

    payload = {
        "memory_id": memory_id,
        "new_content": new_content
    }

    try:
        response = requests.put(f"{API_URL}/memories/update", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Memory '{data['memory_id']}' updated successfully!")
        else:
            print(f"Failed to update memory. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def search_memories():
    print("\n--- Search Memories ---")
    query = input("Enter search query: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return

    user_id = input("Enter user ID to filter (optional): ").strip() or None

    params = {"query": query}
    if user_id:
        params["user_id"] = user_id

    try:
        response = requests.get(f"{API_URL}/memories/search", params=params)
        if response.status_code == 200:
            data = response.json()
            memories = data.get("memories", [])
            if not memories:
                print("No memories found matching the query.")
            else:
                print(f"Found {len(memories)} memory/memories:")
                for mem in memories:
                    print(f"\nMemory ID: {mem['memory_id']}")
                    print(f"User: {mem['user']}")
                    print(f"Content: {mem['content']}")
                    print(f"Metadata: {json.dumps(mem['metadata']) if mem['metadata'] else 'None'}")
                    print(f"Relevance Score: {mem['score']}")
        else:
            print(f"Failed to search memories. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def get_all_memories():
    print("\n--- Get All Memories ---")
    user_id = input("Enter user ID to filter (optional): ").strip() or None

    params = {}
    if user_id:
        params["user_id"] = user_id

    try:
        response = requests.get(f"{API_URL}/memories/all", params=params)
        if response.status_code == 200:
            data = response.json()
            memories = data.get("memories", [])
            if not memories:
                print("No memories found with the specified filters.")
            else:
                print(f"Retrieved {len(memories)} memory/memories:")
                for mem in memories:
                    print(f"\nMemory ID: {mem['memory_id']}")
                    print(f"Content: {mem['content']}")
                    print(f"Metadata: {json.dumps(mem['metadata']) if mem['metadata'] else 'None'}")
                    print(f"Created At: {mem['created_at']}")
                    print(f"Updated At: {mem['updated_at']}")
        else:
            print(f"Failed to retrieve memories. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def get_memory_history():
    print("\n--- Get Memory History ---")
    memory_id = input("Enter Memory ID to retrieve history: ").strip()
    if not memory_id:
        print("Memory ID cannot be empty.")
        return

    try:
        response = requests.get(f"{API_URL}/memories/history/{memory_id}")
        if response.status_code == 200:
            data = response.json()
            history = data.get("history", [])
            if not history:
                print("No history found for the specified Memory ID.")
            else:
                print(f"History for Memory ID '{memory_id}':")
                for record in history:
                    print(f"\nPrevious Value: {record['prev_value']}")
                    print(f"New Value: {record['new_value']}")
                    print(f"Updated At: {record['updated_at']}")
        else:
            print(f"Failed to retrieve history. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

# --- User Management Functions ---

def add_user():
    print("\n--- Add User ---")
    user_id = input("Enter new user ID: ").strip()
    if not user_id:
        print("User ID cannot be empty.")
        return

    metadata_input = input("Enter user metadata as JSON (optional, e.g., {\"name\": \"Alice\", \"email\": \"alice@example.com\"}): ").strip()
    if metadata_input:
        try:
            metadata = json.loads(metadata_input)
        except json.JSONDecodeError:
            print("Invalid JSON format for metadata.")
            return
    else:
        metadata = None

    payload = {
        "user_id": user_id,
        "metadata": metadata
    }

    try:
        response = requests.post(f"{API_URL}/users/add", json=payload)
        if response.status_code == 201:
            data = response.json()
            print(f"User '{data['user_id']}' added successfully!")
        else:
            print(f"Failed to add user. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def search_users():
    print("\n--- Search Users ---")
    user_id = input("Enter user ID to search (supports partial matches): ").strip()
    if not user_id:
        print("User ID cannot be empty.")
        return

    params = {"user_id": user_id}

    try:
        response = requests.get(f"{API_URL}/users/search", params=params)
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            if not users:
                print("No users found matching the search criteria.")
            else:
                print(f"Found {len(users)} user(s):")
                for user in users:
                    print(f"\nUser ID: {user['user_id']}")
                    print(f"Metadata: {json.dumps(user['metadata']) if user['metadata'] else 'None'}")
                    print(f"Created At: {user['created_at']}")
        else:
            print(f"Failed to search users. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def list_all_users():
    print("\n--- List All Users ---")

    try:
        response = requests.get(f"{API_URL}/users/all")
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            if not users:
                print("No users found.")
            else:
                print(f"Total Users: {len(users)}")
                for user in users:
                    print(f"\nUser ID: {user['user_id']}")
                    print(f"Metadata: {json.dumps(user['metadata']) if user['metadata'] else 'None'}")
                    print(f"Created At: {user['created_at']}")
        else:
            print(f"Failed to retrieve users. Status Code: {response.status_code}, Message: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API. Ensure the Flask server is running.")

def exit_client():
    print("\nExiting the Mem0 Text Client. Goodbye!")
    sys.exit(0)

def display_menu():
    print("\n=== Mem0 Text Client ===")
    print("1. Add Memory")
    print("2. Update Memory")
    print("3. Search Memories")
    print("4. Retrieve All Memories")
    print("5. Get Memory History")
    print("6. Add User")
    print("7. Search Users")
    print("8. List All Users")
    print("9. Exit")
    #print("Select an option (1-9):")

def main():
    actions = {
        "1": add_memory,
        "2": update_memory,
        "3": search_memories,
        "4": get_all_memories,
        "5": get_memory_history,
        "6": add_user,
        "7": search_users,
        "8": list_all_users,
        "9": exit_client
    }

    while True:
        display_menu()
        choice = input("Select an option (1-9): ").strip()
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid selection. Please choose a valid option (1-9).")

if __name__ == "__main__":
    main()
