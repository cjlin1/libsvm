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
        self.classifier = RecipeClassifier()
        self.recipes = [
            "pasta tomato basil olive_oil garlic",
            "tortilla beans salsa avocado cilantro",
            "spaghetti meatballs tomato_sauce parmesan",
            "tacos beef lettuce cheese salsa"
        ]
        self.cuisines = ["Italian", "Mexican", "Italian", "Mexican"]

    def test_init(self):
        """
        Test the initialization of the RecipeClassifier.

        This test ensures that a new RecipeClassifier instance has its model
        and vocabulary attributes properly initialized to None.
        """
        self.assertIsNone(self.classifier.model)
        self.assertIsNone(self.classifier.vocabulary)

    def test_preprocess_data(self):
        """
        Test the data preprocessing method of RecipeClassifier.

        This test checks if the preprocess_data method correctly converts
        the input recipes and cuisines into feature matrices and labels.
        """
        X, y = self.classifier.preprocess_data(self.recipes, self.cuisines)
        
        # Check if X is a sparse matrix with correct dimensions
        self.assertEqual(X.shape[0], len(self.recipes))
        self.assertGreater(X.shape[1], 0)
        
        # Check if y is a numpy array with correct length and values
        self.assertIsInstance(y, np.ndarray)
        self.assertEqual(len(y), len(self.cuisines))
        self.assertTrue(all(label in [1, -1] for label in y))

    def test_train(self):
        """
        Test the training method of RecipeClassifier.

        This test checks if the train method successfully trains a model
        and sets the model attribute of the classifier.
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.classifier.train(self.recipes, self.cuisines)
            
            # Check if a warning about small dataset is issued
            self.assertTrue(any("dataset is very small" in str(warning.message) for warning in w))
        
        # Check if a model has been created
        self.assertIsNotNone(self.classifier.model)

    def test_predict(self):
        """
        Test the prediction method of RecipeClassifier.

        This test checks if the predict method returns the expected output
        for new recipes after training the model.
        """
        self.classifier.train(self.recipes, self.cuisines)
        
        new_recipes = [
            "pizza cheese tomato basil",
            "burrito rice beans salsa"
        ]
        predictions = self.classifier.predict(new_recipes)
        
        # Check if predictions are returned for all new recipes
        self.assertEqual(len(predictions), len(new_recipes))
        
        # Check if all predictions are either 'Italian' or 'Mexican'
        self.assertTrue(all(cuisine in ['Italian', 'Mexican'] for cuisine in predictions))

    def test_predict_without_training(self):
        """
        Test prediction without prior training.

        This test ensures that attempting to make predictions without first
        training the model raises a ValueError.
        """
        with self.assertRaises(ValueError):
            self.classifier.predict(["pizza cheese tomato basil"])

if __name__ == '__main__':
    unittest.main()