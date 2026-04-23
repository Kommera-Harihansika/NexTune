"""
Dataset Merger Script

Combines all scraped datasets into a single unified dataset for model training.
"""

import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.enhanced_scraper import EnhancedScraper


def load_and_standardize_datasets():
    """
    Load all available datasets and standardize their formats.
    
    Returns:
        List of standardized DataFrames
    """
    datasets = []
    
    # 1. Load enhanced dataset (already processed)
    print("Loading enhanced-headphones-dataset.csv...")
    df_enhanced = pd.read_csv('data/enhanced-headphones-dataset.csv')
    datasets.append(df_enhanced)
    print(f"  ✓ Loaded {len(df_enhanced)} records")
    
    # 2. Load nexttune cleaned data
    print("\nLoading nexttune-cleaned-data.csv...")
    df_nexttune = pd.read_csv('data/nexttune-cleaned-data.csv')
    
    # Standardize column names
    df_nexttune_std = pd.DataFrame({
        'product_name': df_nexttune['Name'],
        'brand': df_nexttune['Brand'],
        'price_inr': df_nexttune['Price'],
        'rating': df_nexttune['Rating'],
        'review_count': 0,  # Not available in this dataset
        'category': 'unknown',  # Will be detected by enhanced scraper
        'source': 'nexttune_cleaned',
        'battery_life_hrs': None,
        'active_noise_cancellation': None,
        'driver_size_mm': None,
        'bluetooth_version': None,
        'mic_count': None,
        'ipx_rating': None
    })
    
    # Remove rows with price = 0 (invalid data)
    df_nexttune_std = df_nexttune_std[df_nexttune_std['price_inr'] > 0]
    
    datasets.append(df_nexttune_std)
    print(f"  ✓ Loaded {len(df_nexttune_std)} valid records (removed {len(df_nexttune) - len(df_nexttune_std)} with price=0)")
    
    return datasets


def enhance_new_data(df):
    """
    Apply enhanced scraping to extract features from product names.
    
    Args:
        df: DataFrame with product data
        
    Returns:
        Enhanced DataFrame with extracted features
    """
    print("\nEnhancing new data with feature extraction...")
    scraper = EnhancedScraper()
    
    enhanced_records = []
    for idx, row in df.iterrows():
        # Extract features from product name
        features = scraper.extract_with_prompt_engineering(row['product_name'])
        
        # Update row with extracted features
        for key, value in features.items():
            if key in row and (pd.isna(row[key]) or row[key] == 'unknown'):
                row[key] = value
        
        # Simple category detection from product name
        name_lower = str(row['product_name']).lower()
        if 'tws' in name_lower or 'earbuds' in name_lower or 'earpods' in name_lower:
            row['category'] = 'true wireless earbuds'
        elif 'neckband' in name_lower:
            row['category'] = 'neckband'
        elif 'headphone' in name_lower or 'headset' in name_lower:
            row['category'] = 'over-ear headphone'
        
        enhanced_records.append(row)
    
    df_enhanced = pd.DataFrame(enhanced_records)
    print(f"  ✓ Enhanced {len(df_enhanced)} records")
    
    return df_enhanced


def merge_datasets(datasets):
    """
    Merge all datasets into a single unified dataset.
    
    Args:
        datasets: List of DataFrames to merge
        
    Returns:
        Merged DataFrame
    """
    print("\nMerging datasets...")
    
    # Combine all datasets
    df_merged = pd.concat(datasets, ignore_index=True)
    
    # Remove duplicates based on product_name
    initial_count = len(df_merged)
    df_merged = df_merged.drop_duplicates(subset=['product_name'], keep='first')
    duplicates_removed = initial_count - len(df_merged)
    
    print(f"  ✓ Merged {len(datasets)} datasets")
    print(f"  ✓ Total records: {len(df_merged)}")
    print(f"  ✓ Duplicates removed: {duplicates_removed}")
    
    return df_merged


def generate_summary(df):
    """
    Generate and display summary statistics for the merged dataset.
    
    Args:
        df: Merged DataFrame
    """
    print("\n" + "=" * 80)
    print("MERGED DATASET SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Records: {len(df)}")
    print(f"\nPrice Statistics:")
    print(f"  Mean: ₹{df['price_inr'].mean():.2f}")
    print(f"  Median: ₹{df['price_inr'].median():.2f}")
    print(f"  Min: ₹{df['price_inr'].min():.2f}")
    print(f"  Max: ₹{df['price_inr'].max():.2f}")
    
    print(f"\nRating Statistics:")
    print(f"  Mean: {df['rating'].mean():.2f}")
    print(f"  Min: {df['rating'].min():.2f}")
    print(f"  Max: {df['rating'].max():.2f}")
    
    print(f"\nBrands: {df['brand'].nunique()} unique brands")
    print(f"Top 10 brands:")
    for brand, count in df['brand'].value_counts().head(10).items():
        print(f"  {brand}: {count} products")
    
    print(f"\nCategories:")
    for category, count in df['category'].value_counts().items():
        print(f"  {category}: {count} products")
    
    print(f"\nData Sources:")
    for source, count in df['source'].value_counts().items():
        print(f"  {source}: {count} products")
    
    print(f"\nFeature Completeness:")
    for col in ['battery_life_hrs', 'bluetooth_version', 'driver_size_mm', 'active_noise_cancellation']:
        if col in df.columns:
            completeness = (1 - df[col].isna().sum() / len(df)) * 100
            print(f"  {col}: {completeness:.1f}%")
    
    print("=" * 80)


def main():
    """
    Main execution function for merging datasets.
    """
    print("=" * 80)
    print("DATASET MERGER - NexTune Price Prediction")
    print("=" * 80)
    
    # Load all datasets
    datasets = load_and_standardize_datasets()
    
    # Enhance new data with feature extraction
    if len(datasets) > 1:
        datasets[1] = enhance_new_data(datasets[1])
    
    # Merge datasets
    df_final = merge_datasets(datasets)
    
    # Generate summary
    generate_summary(df_final)
    
    # Save merged dataset
    output_file = 'data/final-merged-dataset.csv'
    df_final.to_csv(output_file, index=False)
    print(f"\n✅ Final merged dataset saved to: {output_file}")
    
    # Also update the enhanced dataset for consistency
    df_final.to_csv('data/enhanced-headphones-dataset.csv', index=False)
    print(f"✅ Updated enhanced-headphones-dataset.csv with merged data")


if __name__ == "__main__":
    main()
