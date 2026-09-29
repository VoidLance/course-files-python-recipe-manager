# Recipe Manager

A lightweight, interactive command-line application for creating and managing
recipes. Recipes are saved locally as JSON, so they are available the next time
you run the program.

## Features

- Add recipes with a title, ingredients, and step-by-step instructions.
- Browse recipe titles and search by title or ingredient.
- Read full recipe details.
- Edit recipes while keeping existing ingredients or instructions when desired.
- Delete recipes with a confirmation prompt.
- Store data in a readable JSON file without requiring a database.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Get started

Clone the repository and run the application from its root directory:

```bash
git clone https://github.com/VoidLance/course-files-python-recipe-manager.git
cd course-files-python-recipe-manager
python recipe_manager.py
```

If `python` does not refer to Python 3.10 or newer on your system, use the
appropriate command, such as `python3`.

Choose an option from the numbered menu. For example, select **1. Add recipe**
and enter a title, then enter ingredients one per line. Leave a blank line when
you have finished entering ingredients, and repeat for the instructions. Select
**3. Search recipes** to find recipes by title or ingredient.

## Recipe data

Recipes are stored in [`data/recipes.json`](data/recipes.json), relative to the
application file. The application creates the `data` directory when needed and
handles malformed JSON or invalid recipe entries by reporting the problem in
the terminal.

Each recipe is represented by its title and lists of ingredients and
instructions:

```json
{
  "Vegetable Soup": {
    "ingredients": ["2 carrots", "1 onion", "4 cups vegetable broth"],
    "instructions": ["Chop the vegetables.", "Simmer in broth until tender."]
  }
}
```

Back up this file to preserve your recipes, or edit it directly while keeping
the same JSON structure.

## Help and support

For questions or to report a problem, [open an issue in this
repository](https://github.com/VoidLance/course-files-python-recipe-manager/issues).
Include the Python version and the steps needed to reproduce the issue.

## Maintainers and contributing

This project is maintained by the contributors to
[VoidLance/course-files-python-recipe-manager](https://github.com/VoidLance/course-files-python-recipe-manager).
Contributions are welcome: open an issue to discuss a change, or submit a pull
request with a focused improvement and a clear description. There is no separate
contribution guide in the repository at this time.

There is no license file in the repository currently; check with the project
maintainers before redistributing the project.
