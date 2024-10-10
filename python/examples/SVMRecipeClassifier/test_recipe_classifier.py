"""
Test module for RecipeClassifier

This module contains unit tests for the RecipeClassifier class, which implements
a binary classifier for Italian and Mexican recipes using LIBSVM.

The tests cover the initialization, data preprocessing, training, and prediction
functionalities of the RecipeClassifier.

Note: These tests assume a small dataset and are meant for demonstration purposes.
In a real-world scenario, more comprehensive tests with larger datasets would be necessary.
"""

import unittest
import numpy as np
import warnings
from recipe_classifier import RecipeClassifier

class TestRecipeClassifier(unittest.TestCase):
    """
    A test suite for the RecipeClassifier class.

    This class contains various test methods to ensure the correct functionality
    of the RecipeClassifier, including data preprocessing, model training, and prediction.
    """

    def setUp(self):
        """
        Set up the test environment before each test method.

        This method initializes a RecipeClassifier instance and defines sample
        recipes and cuisines for testing purposes.
        """
        print("\n--- Setting up test environment ---")
        self.classifier = RecipeClassifier()
        self.recipes = [
            "pasta tomato basil olive_oil garlic",
            "tortilla beans salsa avocado cilantro",
            "spaghetti meatballs tomato_sauce parmesan",
            "tacos beef lettuce cheese salsa",
            "pizza mozzarella tomato basil oregano",
            "enchiladas chicken cheese salsa corn",
            "risotto rice parmesan white_wine mushroom",
            "guacamole avocado lime cilantro onion"
        ]
        self.cuisines = ["Italian", "Mexican", "Italian", "Mexican", "Italian", "Mexican", "Italian", "Mexican"]
        print(f"Initialized classifier with {len(self.recipes)} sample recipes")

    def test_init(self):
        """
        Test the initialization of the RecipeClassifier.

        This test ensures that a new RecipeClassifier instance has its model
        and vocabulary attributes properly initialized to None.
        """
        print("\n--- Testing initialization ---")
        print(f"Model: {self.classifier.model}")
        print(f"Vocabulary: {self.classifier.vocabulary}")
        self.assertIsNone(self.classifier.model, "Model should be None upon initialization")
        self.assertIsNone(self.classifier.vocabulary, "Vocabulary should be None upon initialization")
        print("Initialization test passed successfully")

    def test_preprocess_data(self):
        """
        Test the data preprocessing method of RecipeClassifier.

        This test checks if the preprocess_data method correctly converts
        the input recipes and cuisines into feature matrices and labels.
        """
        X, y = self.classifier.preprocess_data(self.recipes, self.cuisines)
        print(f"Preprocessed feature matrix shape: {X.shape}")
        print(f"Label array shape: {y.shape}")
        print(f"Unique labels: {np.unique(y)}")
        # Check if X is a sparse matrix with correct dimensions
        self.assertEqual(X.shape[0], len(self.recipes))
        self.assertGreater(X.shape[1], 0)
        
        # Check if y is a numpy array with correct length and values
        self.assertIsInstance(y, np.ndarray)
        self.assertEqual(len(y), len(self.cuisines))
        self.assertTrue(all(label in [1, -1] for label in y))
        print("Data preprocessing test passed successfully")

    def test_train(self):
        """
        Test the training method of RecipeClassifier.

        This test checks if the train method successfully trains a model
        and sets the model attribute of the classifier.
        """
        print("\n--- Testing model training ---")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.classifier.train(self.recipes, self.cuisines)
            if any("dataset is very small" in str(warning.message) for warning in w):
                print("Warning: Dataset is very small, as expected")
            else:
                print("No warning about small dataset was issued")
        print(f"Model after training: {self.classifier.model}")
        self.assertIsNotNone(self.classifier.model, "Model should not be None after training")
        print("Training test passed successfully")

    def test_predict(self):
        """
        Test the prediction method of RecipeClassifier.

        This test checks if the predict method returns the expected output
        for new recipes after training the model.
        """
        print("\n--- Testing prediction ---")
        self.classifier.train(self.recipes, self.cuisines)
        
        new_recipes = [
            "pizza cheese tomato basil",
            "burrito rice beans salsa"
        ]
        print("Predicting cuisines for new recipes:")
        for recipe in new_recipes:
            print(f"  - {recipe}")
        predictions = self.classifier.predict(new_recipes)
        print("Predictions:", predictions)
        # Check if predictions are returned for all new recipes
        self.assertEqual(len(predictions), len(new_recipes), "Number of predictions should match number of new recipes")
        
        # Check if all predictions are either 'Italian' or 'Mexican'
        self.assertTrue(all(cuisine in ['Italian', 'Mexican'] for cuisine in predictions), "All predictions should be either Italian or Mexican")
        print("Prediction test passed successfully")

    def test_predict_without_training(self):
        """
        Test prediction without prior training.

        This test ensures that attempting to make predictions without first
        training the model raises a ValueError.
        """
        print("\n--- Testing prediction without training ---")
        with self.assertRaises(ValueError):
            self.classifier.predict(["pizza cheese tomato basil"])
        print(f"Raised exception as expected!")
        print("Prediction without training test passed successfully")

    def test_train_and_predict_accuracy(self):
        print("\n--- Testing training and prediction accuracy ---")
        self.classifier.train(self.recipes, self.cuisines)
        predictions = self.classifier.predict(self.recipes)
        accuracy = sum(p == c for p, c in zip(predictions, self.cuisines)) / len(self.cuisines)
        print(f"Training accuracy: {accuracy:.2%}")
        self.assertGreater(accuracy, 0.75, "Training accuracy should be above 75%")
        print("Training and prediction accuracy test passed successfully")

    def test_vocabulary_creation(self):
        print("\n--- Testing vocabulary creation ---")
        self.classifier.train(self.recipes, self.cuisines)
        print(f"Vocabulary size: {len(self.classifier.vocabulary)}")
        self.assertIsNotNone(self.classifier.vocabulary, "Vocabulary should not be None after training")
        expected_ingredients = ["pasta", "tomato", "basil", "olive_oil", "garlic", "tortilla", "beans", "salsa",
                                "avocado", "cilantro"]
        for ingredient in expected_ingredients:
            self.assertIn(ingredient, self.classifier.vocabulary, f"{ingredient} should be in the vocabulary")
            print(f"'{ingredient}' found in vocabulary")
        print("Vocabulary creation test passed successfully")

    def test_predict_new_recipes(self):

        # Train the classifier
        print("\nTraining the classifier...")
        self.classifier.train(self.recipes, self.cuisines)
        print(f"Vocabulary size after training: {len(self.classifier.vocabulary)}")

        # New recipes to test
        new_recipes = [
            "lasagna pasta cheese tomato_sauce beef",
            "burrito rice beans salsa guacamole"
        ]

        print("\nPredicting new recipes:")
        for recipe in new_recipes:
            print(f"Recipe: {recipe}")

        # Predict new recipes
        predictions = self.classifier.predict(new_recipes)

        print("\nPrediction results:")
        for recipe, prediction in zip(new_recipes, predictions):
            print(f"Recipe: {recipe}")
            print(f"Predicted cuisine: {prediction}")

        # Check predictions
        self.assertEqual(predictions[0], "Italian", "Lasagna should be classified as Italian")
        self.assertEqual(predictions[1], "Mexican", "Burrito should be classified as Mexican")

        print("\nTest passed successfully!")

if __name__ == '__main__':
    unittest.main()