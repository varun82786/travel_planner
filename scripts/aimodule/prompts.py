example_json = {
  "username": "username",
  "Title": "Maasan Holi",
  "destination": "Varanasi (3-Day Spiritual & Cultural Escape)",
  "start_date": "2025-03-07",
  "end_date": "2025-03-07",
  "created_at": "2025-03-07",
  "updated_at": None,
  "notes": "Immerse in the mysticism and energy of the oldest living city!",
  "checklist": {
    "Day 1": [
      {
        "item0": "Arrive in Varanasi and check in to a heritage guesthouse by the Ganges.",
        "completed": False
      },
      {
        "item1": "Stroll through the narrow alleys of the Old City and soak in the chaos.",
        "completed": False
      },
      {
        "item2": "Visit the sacred Kashi Vishwanath Temple – feel the divine vibrations.",
        "completed": False
      },
      {
        "item3": "Take a mesmerizing sunset boat ride on the Ganges.",
        "completed": False
      },
      {
        "item4": "Witness the spellbinding Ganga Aarti at Dashashwamedh Ghat.",
        "completed": False
      },
      {
        "item5": "Indulge in street food: Try the famous Banarasi chaat & malaiyyo.",
        "completed": False
      }
    ],
    "Day 2": [
      {
        "item0": "Wake up early for a serene sunrise boat ride along the ghats.",
        "completed": False
      },
      {
        "item1": "Explore the eerie Manikarnika Ghat, where life and death intertwine.",
        "completed": False
      },
      {
        "item2": "If visiting during Holi, experience the Masan Holi with Aghori sadhus.",
        "completed": False
      },
      {
        "item3": "Visit Sarnath, the land of Buddha’s first sermon.",
        "completed": False
      },
      {
        "item4": "Discover local markets for Banarasi silk sarees and souvenirs.",
        "completed": False
      },
      {
        "item5": "Enjoy a soulful evening music performance at a local haveli.",
        "completed": False
      }
    ],
    "Day 3": [
      {
        "item0": "Attend a peaceful morning yoga session on Assi Ghat.",
        "completed": False
      },
      {
        "item1": "Visit hidden gems like Nepali Temple & Kedar Ghat.",
        "completed": False
      },
      {
        "item3": "Say goodbye to the magical city and depart with your heart full of memories.",
        "completed": False
      },
      {
        "item3": "Have a final cup of Banarasi chai with river views.",
        "completed": False
      }
    ]
  },
  "expenses": [],
  "files": [],
  "share": False,
  "itinerary_used": 0
}

user_description = ""
username = ""

itenaryPrompt = """You are a professional travel planner AI. Based on the user's description and form inputs, generate a detailed travel itinerary in valid JSON format only — no explanations, markdown, or extra text.

Use the exact same key structure and nesting style as the example JSON below:

{example_json}

User :
{username}

user preference and description :
{user_description}


Guidelines:
1. Use the example JSON as a strict schema reference.
2. Populate the \"notes\" field with a creative summary based on the user's description.
3. Fill the \"checklist\" section day-wise (\"Day 1\", \"Day 2\", …) with 5–7 meaningful, location-specific, culturally immersive activities per day.
4. Set all checklist items’ `\"completed\"` fields to `false`.
5. Keep \"expenses\", \"files\", and \"share\" fields as in the example.
6. Output must be **ONLY valid JSON** (no code fences or extra text).

Example Output Format:
(Same as example_json but customized for the given inputs)
"""