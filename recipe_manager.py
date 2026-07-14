import json
from dataclasses import dataclass
from pathlib import Path

# Simple terminal recipe manager with JSON persistence.

# Keep persistence relative to this script so the app always uses Recipe Manager/data/.
DATA_DIR = Path(__file__).resolve().parent / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"
MENU_BANNER = r"""
========================================
  ____           _              
 |  _ \ ___  ___(_)_ __   ___   
 | |_) / _ \/ __| | '_ \ / _ \  
 |  _ <  __/ (__| | |_) |  __/  
 |_| \_\___|\___|_| .__/ \___|  
                  |_|           

  __  __                                   
 |  \/  | __ _ _ __   __ _  __ _  ___ _ __ 
 | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
 | |  | | (_| | | | | (_| | (_| |  __/ |   
 |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                            |___/         
                            |Recipe Manager| 
========================================
"""


@dataclass
class Recipe:
    # Represents a recipe stored by title.

    title: str
    ingredients: list[str]
    instructions: list[str]

    def to_dict(self) -> dict[str, list[str]]:
        # Convert a recipe into the JSON shape used on disk.
        return {
            "ingredients": self.ingredients,
            "instructions": self.instructions,
        }

    @classmethod
    def from_dict(cls, title: str, data: dict[str, object]) -> "Recipe":
        # Build a validated recipe from JSON data.
        clean_title = normalize_title(title)
        ingredients = normalize_items(data.get("ingredients"), "ingredients")
        instructions = normalize_items(data.get("instructions"), "instructions")
        return cls(
            title=clean_title,
            ingredients=ingredients,
            instructions=instructions,
        )


Recipes = dict[str, Recipe]


def normalize_title(title: object) -> str:
    # Return a trimmed title or raise if it is invalid.
    if not isinstance(title, str):
        raise ValueError("Recipe title must be text.")
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Recipe title cannot be empty.")
    return clean_title


def normalize_items(values: object, field_name: str) -> list[str]:
    # Validate a non-empty list of non-empty strings.
    if not isinstance(values, list):
        raise ValueError(f"Recipe {field_name} must be a list.")

    cleaned_values: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"Each {field_name[:-1]} must be text.")
        cleaned_value = value.strip()
        if cleaned_value:
            cleaned_values.append(cleaned_value)

    if not cleaned_values:
        raise ValueError(f"Recipe must include at least one {field_name[:-1]}.")

    return cleaned_values


def print_banner() -> None:
    # Render the top-level TUI banner.
    print(MENU_BANNER)


def safe_input(prompt: str) -> str | None:
    # Read input without crashing on Ctrl+C or Ctrl+D.
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return None


def prompt_non_empty(prompt: str, field_name: str) -> str | None:
    # Prompt until a non-empty value is provided or input is cancelled.
    while True:
        value = safe_input(prompt)
        if value is None:
            return None
        clean_value = value.strip()
        if clean_value:
            return clean_value
        print(f"{field_name} cannot be empty.")


def prompt_items(header: str, item_name: str) -> list[str] | None:
    # Collect a non-empty list of items from the user.
    print(header)
    items: list[str] = []
    while True:
        value = safe_input("> ")
        if value is None:
            return None

        clean_value = value.strip()
        if not clean_value:
            if items:
                return items
            print(f"Add at least one {item_name} before finishing.")
            continue

        items.append(clean_value)


def prompt_optional_items(header: str) -> list[str] | None:
    # Collect replacement items while allowing the user to keep current values.
    print(header)
    print("Press Enter immediately to keep the current values.")

    items: list[str] = []
    while True:
        value = safe_input("> ")
        if value is None:
            return None

        clean_value = value.strip()
        if not clean_value:
            return items

        items.append(clean_value)


def display_recipe(recipe: Recipe) -> None:
    # Show the complete details for one recipe.
    print(f"\nTitle: {recipe.title}")
    print("Ingredients:")
    for ingredient in recipe.ingredients:
        print(f"- {ingredient}")
    print("Instructions:")
    for step_number, instruction in enumerate(recipe.instructions, start=1):
        print(f"{step_number}. {instruction}")


def find_recipe_key(recipes: Recipes, title: str) -> str | None:
    # Look up a recipe title without requiring exact casing.
    clean_title = title.strip().lower()
    for recipe_title in recipes:
        if recipe_title.lower() == clean_title:
            return recipe_title
    return None


def find_matches(recipes: Recipes, query: str, include_ingredients: bool = False) -> list[Recipe]:
    # Return recipes that match a title or ingredient search.
    clean_query = query.strip().lower()
    matches: list[Recipe] = []

    for recipe in recipes.values():
        if clean_query in recipe.title.lower():
            matches.append(recipe)
            continue
        if include_ingredients and any(clean_query in ingredient.lower() for ingredient in recipe.ingredients):
            matches.append(recipe)

    return matches


def choose_recipe_from_matches(matches: list[Recipe], action_label: str) -> Recipe | None:
    # Resolve an exact recipe choice when a search returns several matches.
    if len(matches) == 1:
        return matches[0]

    print(f"\nMatching recipes for {action_label}:")
    for recipe in matches:
        print(f"- {recipe.title}")

    selected_title = prompt_non_empty("Enter an exact recipe title: ", "Recipe title")
    if selected_title is None:
        return None

    for recipe in matches:
        if recipe.title.lower() == selected_title.lower():
            return recipe

    print(f"Recipe '{selected_title}' was not in the search results.")
    return None


def load_recipes() -> Recipes:
    # Load recipes from the data directory, skipping invalid entries.
    DATA_DIR.mkdir(exist_ok=True)
    if not RECIPES_FILE.exists():
        return {}

    try:
        with RECIPES_FILE.open("r", encoding="utf-8") as file:
            recipes_data = json.load(file)
    except json.JSONDecodeError as error:
        print(f"Could not read {RECIPES_FILE.name}: invalid JSON ({error.msg}).")
        return {}
    except OSError as error:
        print(f"Could not read {RECIPES_FILE.name}: {error}.")
        return {}

    if not isinstance(recipes_data, dict):
        print(f"Could not read {RECIPES_FILE.name}: top-level JSON must be an object.")
        return {}

    recipes: Recipes = {}
    for title, recipe_data in recipes_data.items():
        if not isinstance(recipe_data, dict):
            print(f"Skipping invalid recipe '{title}': recipe data must be an object.")
            continue

        try:
            recipe = Recipe.from_dict(title, recipe_data)
        except ValueError as error:
            print(f"Skipping invalid recipe '{title}': {error}")
            continue

        recipes[recipe.title] = recipe

    return recipes


def save_recipes(recipes: Recipes) -> bool:
    # Persist recipes atomically to the data directory.
    DATA_DIR.mkdir(exist_ok=True)
    temp_file = RECIPES_FILE.with_suffix(".tmp")
    recipes_data = {
        title: recipe.to_dict()
        for title, recipe in sorted(recipes.items())
    }

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(recipes_data, file, indent=2)
        # Replace the old file only after the new JSON has been written fully.
        temp_file.replace(RECIPES_FILE)
    except OSError as error:
        print(f"Could not save recipes: {error}.")
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        return False

    return True


def add_recipe(recipes: Recipes) -> None:
    # Create a new recipe after validating all required fields.
    title = prompt_non_empty("Enter recipe title: ", "Recipe title")
    if title is None:
        return

    if find_recipe_key(recipes, title) is not None:
        print(f"Recipe '{title}' already exists.")
        return

    ingredients = prompt_items("Enter ingredients (leave blank to finish):", "ingredient")
    if ingredients is None:
        return

    instructions = prompt_items("Enter instructions (leave blank to finish):", "instruction")
    if instructions is None:
        return

    recipe = Recipe(title=title, ingredients=ingredients, instructions=instructions)
    recipes[recipe.title] = recipe
    if save_recipes(recipes):
        print(f"Recipe '{recipe.title}' added successfully!")


def view_recipes(recipes: Recipes) -> None:
    # List all recipe titles currently in memory.
    if not recipes:
        print("No recipes found.")
        return

    print("\nAvailable recipes:")
    for recipe in sorted(recipes.values(), key=lambda recipe: recipe.title.lower()):
        print(f"- {recipe.title}")


def search_recipes(recipes: Recipes) -> None:
    # Search recipe titles and ingredients without opening a full recipe.
    if not recipes:
        print("No recipes found.")
        return

    query = prompt_non_empty("Enter search query: ", "Search query")
    if query is None:
        return

    matches = find_matches(recipes, query, include_ingredients=True)
    if not matches:
        print(f"No recipes found for '{query}'.")
        return

    print(f"\nRecipes matching '{query}':")
    for recipe in sorted(matches, key=lambda recipe: recipe.title.lower()):
        print(f"- {recipe.title}")


def read_recipe(recipes: Recipes) -> None:
    # Search by title and print the full recipe details.
    if not recipes:
        print("No recipes found.")
        return

    query = prompt_non_empty("Enter recipe title to read: ", "Recipe title")
    if query is None:
        return

    matches = find_matches(recipes, query)
    if not matches:
        print(f"No recipes found for '{query}'.")
        return

    selected_recipe = choose_recipe_from_matches(matches, "reading")
    if selected_recipe is not None:
        display_recipe(selected_recipe)


def edit_recipe(recipes: Recipes) -> None:
    # Update an existing recipe while preserving current data by default.
    if not recipes:
        print("No recipes found.")
        return

    title = prompt_non_empty("Enter recipe title to edit: ", "Recipe title")
    if title is None:
        return

    recipe_key = find_recipe_key(recipes, title)
    if recipe_key is None:
        print(f"Recipe '{title}' not found.")
        return

    recipe = recipes[recipe_key]
    print(f"\nEditing recipe '{recipe.title}':")
    display_recipe(recipe)

    new_ingredients = prompt_optional_items("Enter replacement ingredients:")
    if new_ingredients is None:
        return

    new_instructions = prompt_optional_items("Enter replacement instructions:")
    if new_instructions is None:
        return

    recipe.ingredients = new_ingredients or recipe.ingredients
    recipe.instructions = new_instructions or recipe.instructions
    if save_recipes(recipes):
        print(f"Recipe '{recipe.title}' updated successfully!")


def delete_recipe(recipes: Recipes) -> None:
    # Delete an existing recipe after explicit confirmation.
    if not recipes:
        print("No recipes found.")
        return

    title = prompt_non_empty("Enter recipe title to delete: ", "Recipe title")
    if title is None:
        return

    recipe_key = find_recipe_key(recipes, title)
    if recipe_key is None:
        print(f"Recipe '{title}' not found.")
        return

    confirmation = prompt_non_empty(
        f"Type '{recipe_key}' to confirm deletion: ",
        "Confirmation",
    )
    if confirmation is None:
        return

    if confirmation.lower() != recipe_key.lower():
        print("Deletion cancelled.")
        return

    del recipes[recipe_key]
    if save_recipes(recipes):
        print(f"Recipe '{recipe_key}' deleted successfully!")


def main() -> None:
    # Run the terminal recipe manager.
    recipes = load_recipes()
    menu_actions = {
        "1": add_recipe,
        "2": view_recipes,
        "3": search_recipes,
        "4": read_recipe,
        "5": edit_recipe,
        "6": delete_recipe,
    }

    while True:
        print_banner()
        print("1. Add recipe")
        print("2. View recipes")
        print("3. Search recipes")
        print("4. Read recipe")
        print("5. Edit recipe")
        print("6. Delete recipe")
        print("7. Exit")

        choice = safe_input("Enter your choice (1-7): ")
        if choice is None or choice.strip() == "7":
            print("Goodbye!")
            break

        action = menu_actions.get(choice.strip())
        if action is None:
            print("Invalid choice. Enter a number from 1 to 7.")
            continue

        action(recipes)


if __name__ == "__main__":
    main()
