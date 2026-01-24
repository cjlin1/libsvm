"""
Recipe Classifier using LIBSVM

This module implements a binary classifier for Italian and Mexican recipes
using LIBSVM. It's intended as a demonstration of how to use LIBSVM for
text classification tasks.

WARNING: Due to the extremely small dataset, this model overfits and does not
generalize well. This implementation is for demonstration purposes only and
should not be used for real-world applications without significant modifications.
"""

from libsvm.svmutil import *
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import warnings

class RecipeClassifier:
    """A binary classifier for Italian and Mexican recipes using LIBSVM."""

    def __init__(self):
        """Initialize the RecipeClassifier."""
        self.model = None
        self.vocabulary = None

    def preprocess_data(self, recipes, cuisines):
        """
        Preprocess the recipe data for LIBSVM.

        Args:
            recipes (list): List of recipe ingredient strings.
            cuisines (list): List of cuisine labels ('Italian' or 'Mexican').

        Returns:
            tuple: (X, y) where X is a sparse matrix of features and y is an array of labels.
        """
        # Create vocabulary
        if self.vocabulary is None:
            all_ingredients = set(' '.join(recipes).split())
            self.vocabulary = {ingredient: idx for idx, ingredient in enumerate(all_ingredients)}

        # Convert recipes to feature vectors
        rows, cols, data = [], [], []
        for idx, recipe in enumerate(recipes):
            for ingredient in recipe.split():
                if ingredient in self.vocabulary:
                    rows.append(idx)
                    cols.append(self.vocabulary[ingredient])
                    data.append(1)
        
        X = csr_matrix((data, (rows, cols)), shape=(len(recipes), len(self.vocabulary)))
        y = np.array([1 if cuisine == 'Italian' else -1 for cuisine in cuisines])
        return X, y

    def train(self, recipes, cuisines):
        """
        Train the SVM model.

        Args:
            recipes (list): List of recipe ingredient strings.
            cuisines (list): List of cuisine labels ('Italian' or 'Mexican').
        """
        if len(recipes) < 20:
            warnings.warn("The dataset is very small. The model is likely to overfit.")
        
        X, y = self.preprocess_data(recipes, cuisines)
        
        # Split data into training and validation sets
        np.random.seed(42)
        indices = np.random.permutation(len(recipes))
        split = int(0.8 * len(recipes))
        train_idx, val_idx = indices[:split], indices[split:]
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        
        # Convert to LIBSVM format
        prob = svm_problem(y_train.tolist(), X_train.toarray().tolist())
        param = svm_parameter('-t 0 -c 0.1')  # Linear kernel, C=0.1 for less overfitting
        self.model = svm_train(prob, param)
        
        # Validate the model
        p_labels, _, _ = svm_predict(y_val.tolist(), X_val.toarray().tolist(), self.model)
        accuracy = sum(1 for i, j in zip(p_labels, y_val) if i == j) / len(y_val)
        print(f"Validation Accuracy: {accuracy:.2f}")
        
        if accuracy == 1.0:
            warnings.warn("Perfect validation accuracy suggests overfitting.")

    def predict(self, new_recipes):
        """
        Predict cuisines for new recipes.

        Args:
            new_recipes (list): List of new recipe ingredient strings.

        Returns:
            list: Predicted cuisines ('Italian' or 'Mexican').
        """
        if self.model is None:
            raise ValueError("Model has not been trained. Call train() first.")
        
        X, _ = self.preprocess_data(new_recipes, [None] * len(new_recipes))
        p_labels, _, _ = svm_predict([0] * X.shape[0], X.toarray().tolist(), self.model)
        return ['Italian' if label > 0 else 'Mexican' for label in p_labels]


def main():
    """Demonstrate the usage of RecipeClassifier."""
    classifier = RecipeClassifier()
    
    # Sample data
    recipes = [
        "pasta tomato basil olive_oil garlic",
        "tortilla beans salsa avocado cilantro",
        "spaghetti meatballs tomato_sauce parmesan",
        "tacos beef lettuce cheese salsa",
        "pizza mozzarella tomato basil oregano",
        "enchiladas chicken cheese salsa corn",
        "lasagna pasta beef tomato cheese",
        "quesadilla tortilla cheese beans salsa",
        "risotto rice parmesan white_wine",
        "guacamole avocado lime cilantro onion"
    ]
    cuisines = ["Italian", "Mexican", "Italian", "Mexican", "Italian", "Mexican", "Italian", "Mexican", "Italian", "Mexican"]
    
    # Train the model
    classifier.train(recipes, cuisines)
    
    # Predict new recipes
    new_recipes = [
        "pizza cheese tomato basil oregano",
        "burrito rice beans salsa guacamole"
    ]
    predictions = classifier.predict(new_recipes)
    print("Predictions for new recipes:", predictions)

    # Evaluate on training data
    train_predictions = classifier.predict(recipes)
    accuracy = sum(1 for pred, true in zip(train_predictions, cuisines) if pred == true) / len(cuisines)
    print(f"Training Accuracy: {accuracy:.2f}")
    
    print("\nWARNING: This model is overfitting due to the small dataset.")
    print("For a real-world application, consider the following improvements:")
    print("1. Collect a much larger and more diverse dataset.")
    print("2. Use cross-validation for more robust evaluation.")
    print("3. Implement feature engineering specific to recipe classification.")
    print("4. Experiment with different ML algorithms and hyperparameters.")

if __name__ == "__main__":
    main()