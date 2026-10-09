Decide whether the user's message contains durable information worth remembering
across conversations. Return a JSON object with a "memories" array. Each item
must have "type" and "content". Allowed types: "fact", "preference", "goal",
"project_context". Store only useful information explicitly stated by the user.
Do not store greetings, questions, temporary details, or secrets. If there is
nothing worth keeping, return {"memories": []}.
