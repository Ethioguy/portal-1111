"""Simple, high-protein, whole-food recipes that fit the training plan.

Shared by the web app (built in by tools/build_recipes.py) and available to the AI layer.
General nutrition ideas, not medical or dietary advice; check labels for allergies."""
from __future__ import annotations

RECIPES = [
    {"id": "green-smoothie", "title": "Daily green smoothie", "when": "Any time; easy daily habit", "serves": "2–3 glasses (keeps 48 h)",
     "tags": ["daily", "plant-based", "no-cook"],
     "ingredients": ["A big handful or two of leafy greens (spinach, kale, any mix)", "1 ripe avocado", "1–2 celery stalks",
                     "1 cucumber", "1 tbsp seeds (chia, hemp or ground flax)", "Cold water to cover",
                     "Optional for sweetness: ½ mango, 1 apple or 1 carrot"],
     "steps": ["Add everything except the water to the blender.", "Pour in water to just cover the ingredients.",
               "Blend 1–2 minutes until smooth; add water for a thinner drink.", "Drink now or keep in sealed jars in the fridge for up to 48 hours."],
     "tip": "Use whatever greens and fruit are in season. Add a scoop of protein powder or Greek yogurt to make it a meal."},
    {"id": "recovery-smoothie", "title": "Recovery protein smoothie", "when": "Within an hour after a workout", "serves": "1",
     "tags": ["post-workout", "high-protein", "no-cook"],
     "ingredients": ["1 scoop protein powder or ¾ cup plain Greek yogurt", "1 banana (frozen is best)", "1 cup milk or soy milk",
                     "1 tbsp peanut butter", "2 tbsp rolled oats", "Handful of ice"],
     "steps": ["Blend everything for 45 seconds.", "Drink within an hour of training."],
     "tip": "Protein plus carbohydrate after hard sessions supports recovery. Use a dairy-free milk if you need to."},
    {"id": "overnight-oats", "title": "Overnight protein oats", "when": "Breakfast, prepped the night before", "serves": "1",
     "tags": ["breakfast", "high-protein", "meal-prep"],
     "ingredients": ["½ cup rolled oats", "½ cup Greek yogurt", "½ cup milk", "1 tbsp chia seeds", "Berries and a little honey to taste"],
     "steps": ["Stir oats, yogurt, milk and chia in a jar.", "Refrigerate overnight.", "Top with berries in the morning."],
     "tip": "Make three jars on Sunday for the week's early runs."},
    {"id": "teff-porridge", "title": "Teff porridge", "when": "Breakfast or pre-run fuel", "serves": "2",
     "tags": ["breakfast", "gluten-free", "whole-grain"],
     "ingredients": ["½ cup whole-grain teff", "2 cups water or milk", "Pinch of salt", "Cinnamon or cardamom",
                     "Toppings: sliced banana, nuts, a spoon of nut butter or yogurt"],
     "steps": ["Bring the liquid and salt to a boil, then stir in the teff.", "Simmer on low for about 15–20 minutes, stirring often, until thick and creamy.",
               "Stir in the spice and add toppings."],
     "tip": "Teff is naturally gluten-free and gives steady energy; cook a double batch and reheat with a splash of milk."},
    {"id": "egg-scramble", "title": "Egg and vegetable scramble", "when": "Breakfast or quick dinner", "serves": "1",
     "tags": ["high-protein", "quick", "low-carb"],
     "ingredients": ["3 eggs (or 2 eggs + 2 whites)", "Handful of spinach", "½ bell pepper, diced", "¼ onion, diced", "1 tsp olive oil", "Salt, pepper, chili flakes"],
     "steps": ["Soften onion and pepper in the oil for 3 minutes.", "Add spinach until it wilts.", "Pour in the beaten eggs and stir gently until just set; season."],
     "tip": "Serve with whole-grain toast or teff injera on training days."},
    {"id": "sheet-pan-chicken", "title": "Sheet-pan chicken and vegetables", "when": "Dinner; leftovers for lunch", "serves": "3",
     "tags": ["high-protein", "meal-prep", "dinner"],
     "ingredients": ["1 lb (450 g) chicken breast or thighs, cut in pieces", "1 sweet potato, cubed", "2 cups broccoli florets",
                     "1 red onion, in wedges", "1½ tbsp olive oil", "1 tsp each paprika, garlic powder, cumin; salt and pepper"],
     "steps": ["Heat the oven to 425°F (220°C).", "Toss everything with the oil and spices on a lined tray in one layer.",
               "Roast 25–30 minutes until the chicken is cooked through (165°F / 74°C inside) and the vegetables are browned."],
     "tip": "Swap chicken for tofu or chickpeas for a plant-based tray."},
    {"id": "red-lentil-stew", "title": "Red lentil stew", "when": "Dinner; freezes well", "serves": "4",
     "tags": ["plant-based", "high-fibre", "meal-prep"],
     "ingredients": ["1 cup red lentils, rinsed", "1 onion, finely chopped", "2 garlic cloves, 1 tsp grated ginger", "1–2 tbsp berbere or mild curry spice",
                     "1 tbsp oil", "1 can chopped tomatoes", "3 cups water or stock", "Salt; spinach to finish"],
     "steps": ["Cook the onion in the oil until soft; add garlic, ginger and spice for 1 minute.", "Add lentils, tomatoes and water; simmer 20–25 minutes, stirring, until thick.",
               "Stir in spinach, season and serve with teff injera, rice or bread."],
     "tip": "Lentils give protein and fibre for long energy. Add a side of yogurt or eggs for extra protein."},
]


def for_day(dow: int) -> list[str]:
    """Suggested recipe ids for a weekday (0 = Sunday ... 6 = Saturday): the daily smoothie plus one meal idea."""
    meals = ["red-lentil-stew", "overnight-oats", "sheet-pan-chicken", "teff-porridge", "egg-scramble", "sheet-pan-chicken", "recovery-smoothie"]
    return ["green-smoothie", meals[dow % 7]]


def export_for_web() -> dict:
    return {"items": RECIPES, "byDay": {str(d): for_day(d) for d in range(7)}}
