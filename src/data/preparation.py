"""
Data Preparation Module for Bluetooth Headphones Price Prediction

This module handles data loading, cleaning, feature engineering, and preprocessing
for the price prediction model.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparation:
    """
    Handles all data preparation tasks including:
    - Loading data
    - Handling missing values
    - Removing duplicates
    - Feature engineering
    - Encoding categorical variables
    - Train-test splitting
    - Feature scaling
    """
    
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler: StandardScaler = StandardScaler()
        self.feature_columns: List[str] = []
        self.target_column: str = 'price_inr'
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load dataset from CSV file.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values using appropriate strategies:
        - Drop rows with missing price or brand (critical features)
        - Impute battery_life with median by category
        - Impute bluetooth_version with mode
        - Impute driver_size with median by category
        - Fill rating with median
        - Fill review_count with 0
        - Fill active_noise_cancellation with 0
        - Fill mic_count with 2 (standard)
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        logger.info("Handling missing values")
        df_clean = df.copy()
        
        # Drop rows with missing critical features
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['price_inr', 'brand'])
        logger.info(f"Removed {initial_count - len(df_clean)} rows with missing price/brand")
        
        # Impute numerical features
        if 'battery_life_hrs' in df_clean.columns:
            df_clean['battery_life_hrs'] = df_clean.groupby('category')['battery_life_hrs'].transform(
                lambda x: x.fillna(x.median())
            )
        
        if 'bluetooth_version' in df_clean.columns:
            mode_value = df_clean['bluetooth_version'].mode()
            if len(mode_value) > 0:
                df_clean['bluetooth_version'] = df_clean['bluetooth_version'].fillna(mode_value[0])
        
        if 'driver_size_mm' in df_clean.columns:
            df_clean['driver_size_mm'] = df_clean.groupby('category')['driver_size_mm'].transform(
                lambda x: x.fillna(x.median())
            )
        
        if 'rating' in df_clean.columns:
            df_clean['rating'] = df_clean['rating'].fillna(df_clean['rating'].median())
        
        if 'review_count' in df_clean.columns:
            df_clean['review_count'] = df_clean['review_count'].fillna(0)
        
        if 'active_noise_cancellation' in df_clean.columns:
            df_clean['active_noise_cancellation'] = df_clean['active_noise_cancellation'].fillna(0)
        
        if 'mic_count' in df_clean.columns:
            df_clean['mic_count'] = df_clean['mic_count'].fillna(2)
        
        logger.info("Missing values handled successfully")
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records based on product_name.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with duplicates removed
        """
        logger.info("Removing duplicates")
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=['product_name'], keep='first')
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate records")
        return df_clean
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features from existing ones:
        - has_noise_cancellation: Binary indicator for ANC
        - price_per_hour: Price divided by battery life
        - brand_tier: Categorize brands as budget/mid/premium
        - bluetooth_major_version: Extract major version number
        - high_rating: Binary indicator for rating >= 4.0
        - has_ipx_rating: Binary indicator for water resistance
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features")
        df_eng = df.copy()
        
        # has_noise_cancellation
        if 'active_noise_cancellation' in df_eng.columns:
            df_eng['has_noise_cancellation'] = (df_eng['active_noise_cancellation'] == 1).astype(int)
        
        # price_per_hour
        if 'battery_life_hrs' in df_eng.columns:
            df_eng['price_per_hour'] = df_eng['price_inr'] / (df_eng['battery_life_hrs'] + 1)
        
        # brand_tier
        if 'brand' in df_eng.columns:
            brand_avg_price = df_eng.groupby('brand')['price_inr'].mean()
            
            def categorize_brand(brand):
                if brand not in brand_avg_price:
                    return 'mid'
                avg_price = brand_avg_price[brand]
                if avg_price >= 10000:
                    return 'premium'
                elif avg_price >= 3000:
                    return 'mid'
                else:
                    return 'budget'
            
            df_eng['brand_tier'] = df_eng['brand'].apply(categorize_brand)
        
        # bluetooth_major_version
        if 'bluetooth_version' in df_eng.columns:
            df_eng['bluetooth_major_version'] = df_eng['bluetooth_version'].apply(
                lambda x: int(x) if pd.notna(x) else 5
            )
        
        # high_rating
        if 'rating' in df_eng.columns:
            df_eng['high_rating'] = (df_eng['rating'] >= 4.0).astype(int)
        
        # has_ipx_rating
        if 'ipx_rating' in df_eng.columns:
            df_eng['has_ipx_rating'] = df_eng['ipx_rating'].notna().astype(int)
        
        logger.info(f"Created {6} new features")
        return df_eng
    
    def encode_categorical(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical features using LabelEncoder.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit new encoders (True for training, False for inference)
            
        Returns:
            DataFrame with encoded categorical features
        """
        logger.info("Encoding categorical features")
        df_enc = df.copy()
        
        categorical_features = ['category', 'brand', 'brand_tier']
        
        for feature in categorical_features:
            if feature in df_enc.columns:
                if fit:
                    le = LabelEncoder()
                    df_enc[f'{feature}_encoded'] = le.fit_transform(df_enc[feature])
                    self.label_encoders[feature] = le
                else:
                    if feature in self.label_encoders:
                        le = self.label_encoders[feature]
                        # Handle unseen labels
                        df_enc[f'{feature}_encoded'] = df_enc[feature].apply(
                            lambda x: le.transform([x])[0] if x in le.classes_ else -1
                        )
        
        logger.info(f"Encoded {len(categorical_features)} categorical features")
        return df_enc
    
    def normalize_numerical(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """
        Normalize numerical features using StandardScaler.
        
        Args:
            X: Feature matrix
            fit: Whether to fit the scaler (True for training, False for inference)
            
        Returns:
            Normalized feature matrix
        """
        logger.info("Normalizing numerical features")
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        logger.info(f"Normalized features - Mean: {X_scaled.mean():.4f}, Std: {X_scaled.std():.4f}")
        return X_scaled
    
    def create_train_test_split(
        self, 
        X: pd.DataFrame, 
        y: pd.Series, 
        test_size: float = 0.2, 
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into training and test sets.
        
        Args:
            X: Feature matrix
            y: Target vector
            test_size: Proportion of data for test set (default: 0.2)
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        logger.info(f"Creating train-test split with test_size={test_size}")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
        logger.info(f"Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare feature matrix and target vector for modeling.
        
        Args:
            df: Input DataFrame with all features
            
        Returns:
            Tuple of (X, y) where X is feature matrix and y is target vector
        """
        self.feature_columns = [
            'category_encoded',
            'brand_encoded',
            'brand_tier_encoded',
            'rating',
            'review_count',
            'battery_life_hrs',
            'driver_size_mm',
            'bluetooth_version',
            'bluetooth_major_version',
            'mic_count',
            'has_noise_cancellation',
            'has_ipx_rating',
            'high_rating',
            'price_per_hour'
        ]
        
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        logger.info(f"Prepared features: {X.shape}, target: {y.shape}")
        return X, y
    
    def full_pipeline(
        self, 
        filepath: str, 
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Execute the complete data preparation pipeline.
        
        Args:
            filepath: Path to the raw data CSV
            test_size: Proportion of data for test set
            
        Returns:
            Tuple of (X_train_scaled, X_test_scaled, y_train, y_test)
        """
        logger.info("=" * 80)
        logger.info("STARTING FULL DATA PREPARATION PIPELINE")
        logger.info("=" * 80)
        
        # Load data
        df = self.load_data(filepath)
        
        # Clean data
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Encode categorical features
        df = self.encode_categorical(df, fit=True)
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        # Train-test split
        X_train, X_test, y_train, y_test = self.create_train_test_split(X, y, test_size)
        
        # Normalize features
        X_train_scaled = self.normalize_numerical(X_train, fit=True)
        X_test_scaled = self.normalize_numerical(X_test, fit=False)
        
        logger.info("=" * 80)
        logger.info("DATA PREPARATION PIPELINE COMPLETED")
        logger.info("=" * 80)
        
        return X_train_scaled, X_test_scaled, y_train.values, y_test.values


if __name__ == "__main__":
    # Example usage
    prep = DataPreparation()
    X_train, X_test, y_train, y_test = prep.full_pipeline(
        filepath='data/enhanced-headphones-dataset.csv'
    )
    
    print(f"\nPipeline Results:")
    print(f"  X_train shape: {X_train.shape}")
    print(f"  X_test shape: {X_test.shape}")
    print(f"  y_train shape: {y_train.shape}")
    print(f"  y_test shape: {y_test.shape}")
