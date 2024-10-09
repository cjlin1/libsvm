# Binary Recipe Classifier using LIBSVM

This project implements a binary recipe classifier using LIBSVM. It classifies recipes as either Italian or Mexican cuisine based on their ingredients. It serves as a demonstration of applying Support Vector Machines (SVM) to text classification tasks, specifically in the domain of recipe categorization.

## Key Features

- Binary classification of recipes (Italian vs Mexican)
- Utilizes LIBSVM for efficient SVM implementation
- Preprocesses text-based recipe data into numerical features
- Includes a comprehensive test suite for validation

## Requirements

- Python 3.7+
- NumPy
- SciPy
- LIBSVM


## Usage

To use the RecipeClassifier in your Python script:

```python
from recipe_classifier import RecipeClassifier

# Initialize the classifier
classifier = RecipeClassifier()

# Train the classifier
recipes = [
    "pasta tomato basil olive_oil garlic",
    "tortilla beans salsa avocado cilantro",
    "pizza cheese tomato oregano",
    "tacos beef lettuce cheese salsa"
]
cuisines = ["Italian", "Mexican", "Italian", "Mexican"]
classifier.train(recipes, cuisines)

# Make predictions
new_recipes = ["lasagna pasta cheese tomato_sauce beef", "burrito rice beans salsa guacamole"]
predictions = classifier.predict(new_recipes)
print(predictions)