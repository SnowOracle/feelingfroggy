"""
Frog species identifier module for the Feeling Froggy app.
This is a simplified demonstration that doesn't use actual machine learning.
In a real implementation, you would use a trained model for classification.
"""

import pandas as pd
import os
import random

class FrogIdentifier:
    """
    A simple frog species identifier class.
    """
    
    def __init__(self, data_path="data/frog_species.csv"):
        """
        Initialize the identifier with frog species data.
        
        Args:
            data_path (str): Path to the CSV file with frog species data.
        """
        self.data_path = data_path
        self.species_data = None
        self.load_data()
    
    def load_data(self):
        """Load the frog species data from CSV."""
        if os.path.exists(self.data_path):
            self.species_data = pd.read_csv(self.data_path)
        else:
            raise FileNotFoundError(f"Frog species data file not found at {self.data_path}")
    
    def identify_from_image(self, image=None):
        """
        Identify frog species from an image.
        This is a mock implementation that returns random results.
        
        Args:
            image: The image to identify (not used in this mock implementation).
            
        Returns:
            dict: A dictionary with identified species information and confidence scores.
        """
        if self.species_data is None:
            self.load_data()
        
        # In a real implementation, you would process the image and use a model for prediction
        # For demonstration, we'll just select a random species and add confidence scores
        
        # Select 3 random species
        if len(self.species_data) < 3:
            num_species = len(self.species_data)
        else:
            num_species = 3
            
        selected_indices = random.sample(range(len(self.species_data)), num_species)
        results = []
        
        # Generate confidence scores that sum to 100%
        confidence_scores = self._generate_random_confidence_scores(num_species)
        
        for i, idx in enumerate(selected_indices):
            species = self.species_data.iloc[idx]
            result = {
                'name': species['name'],
                'scientific_name': species['scientific_name'],
                'confidence': confidence_scores[i],
                'image_url': species['image_url'],
                'habitat': species['habitat'],
                'region': species['region'],
                'conservation_status': species['conservation_status']
            }
            results.append(result)
        
        return {
            'results': results,
            'message': 'Identification complete. Here are the most likely matches.'
        }
    
    def _generate_random_confidence_scores(self, num_scores):
        """Generate random confidence scores that sum to 100%."""
        scores = [random.random() for _ in range(num_scores)]
        total = sum(scores)
        normalized_scores = [round(score / total * 100, 1) for score in scores]
        
        # Make sure they sum to 100 (fix any rounding issues)
        if sum(normalized_scores) != 100:
            normalized_scores[-1] += 100 - sum(normalized_scores)
            
        # Sort in descending order
        normalized_scores.sort(reverse=True)
        return normalized_scores

# Example usage
if __name__ == "__main__":
    identifier = FrogIdentifier()
    results = identifier.identify_from_image()
    print(results) 