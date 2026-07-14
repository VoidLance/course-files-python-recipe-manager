# Recipe Manager

Recipe Manager is a small terminal application for storing and maintaining recipes in JSON format.

## Features

- Add recipes with validated titles, ingredients, and instructions
- View all saved recipe titles
- Search recipes by title or ingredient
- Read the full details of a recipe by searching its title
- Edit or delete recipes with basic safety checks
- Persist recipes in `data/recipes.json`

## How to run

From the `Recipe Manager` directory:

```bash
python recipe_manager.py
```

## How it stores data

- Recipes are loaded from `data/recipes.json`
- The `data` directory is created automatically if it does not exist
- Invalid JSON or malformed recipe entries are handled gracefully and reported in the terminal

## Menu overview

1. **Add recipe**: create a new recipe
2. **View recipes**: list all recipe titles
3. **Search recipes**: find recipe titles by title or ingredient
4. **Read recipe**: search by title and show the full recipe
5. **Edit recipe**: replace ingredients and instructions for an existing recipe
6. **Delete recipe**: remove a recipe after confirmation
7. **Exit**: close the application
