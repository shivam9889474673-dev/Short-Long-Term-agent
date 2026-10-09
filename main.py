from agent import ask_soul, short_memory
from memory.long_term import (delete_memory,get_memories,initialize_database,)
def main():
    initialize_database()

    print("SOUL AI is ready. Type 'exit' to quit.")
    print("Commands: /memories, /forget <id>, exit")
    session_id = "cli-session"
    print("Short-term memory when starting:", short_memory.get_messages(session_id))
    print("Long-term memories when starting:", get_memories(session_id))

    while True:
        try:
            user_message = input("\nYou: ").strip()

            if user_message.lower() == "exit":
                print("Soul: Goodbye!")
                break
            if not user_message:
                continue
            if user_message == "/memories":
                memories = get_memories(session_id)
                if not memories:
                    print("No long-term memories stored.")
                else:
                    for memory in memories:
                        print(
                            f"ID {memory['id']} [{memory['memory_type']}]: "
                            f"{memory['content']}"
                        )
                continue
            if user_message.startswith("/forget"):
                command, _, memory_id_text = user_message.partition(" ")
                if command != "/forget" or not memory_id_text.strip():
                    print("Usage: /forget <memory-id> (list IDs with /memories)")
                    continue
                try:
                    memory_id = int(memory_id_text.strip())
                except ValueError:
                    print("Memory ID must be a number.")
                    continue

                if delete_memory(memory_id, session_id):
                    print(f"Deleted long-term memory {memory_id}.")
                else:
                    print(f"No long-term memory found with ID {memory_id}.")
                continue

            answer = ask_soul(user_message, session_id)
            print(f"Soul: {answer}")
            print("\n--- SHORT-TERM MEMORY ---")
            print(short_memory.get_messages(session_id))
            print("\n--- LONG-TERM MEMORY ---")
            print(get_memories(session_id))

        except KeyboardInterrupt:
            print("\nSoul: Goodbye!")
            break
        except Exception as error:
            print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
