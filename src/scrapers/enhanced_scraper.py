"""
Enhanced Web Scraper with Prompt Engineering
Extracts and normalizes headphone data from e-commerce platforms using regex patterns
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedScraper:
    """
    Enhanced scraper that uses prompt engineering (regex patterns) to extract
    structured data from unstructured product descriptions
    """
    
    # Regex patterns for extracting features from unstructured text
    EXTRACTION_PATTERNS = {
        'battery_life': r'(\d+)\s*(?:hours?|hrs?|h|hr)\s*(?:battery|playtime|playback|music)?',
        'bluetooth_version': r'bluetooth\s*(?:version|v)?\s*([0-9]\.[0-9])',
        'driver_size': r'(\d+)\s*mm\s*driver',
        'frequency_response': r'(\d+)\s*hz\s*-\s*(\d+)\s*(?:khz|hz)',
        'weight': r'(\d+)\s*(?:grams?|g)\s*weight',
        'anc_db': r'(\d+)\s*db\s*(?:anc|noise)',
        'mic_count': r'(\d+)\s*mic',
        'ipx_rating': r'ipx(\d+)',
    }
    
    def __init__(self):
        """Initialize the enhanced scraper"""
        self.stats = {
            'total_processed': 0,
            'features_extracted': 0,
            'normalization_applied': 0
        }
    
    def extract_with_prompt_engineering(self, text: str) -> Dict[str, any]:
        """
        Extract structured data from unstructured text using regex patterns
        
        Args:
            text: Unstructured product description text
            
        Returns:
            Dictionary with extracted features
        """
        if not text or not isinstance(text, str):
            return {}
        
        text_lower = text.lower()
        extracted = {}
        
        # Extract battery life
        battery_match = re.search(self.EXTRACTION_PATTERNS['battery_life'], text_lower, re.IGNORECASE)
        if battery_match:
            extracted['battery_life_hrs'] = float(battery_match.group(1))
            self.stats['features_extracted'] += 1
        
        # Extract Bluetooth version
        bt_match = re.search(self.EXTRACTION_PATTERNS['bluetooth_version'], text_lower, re.IGNORECASE)
        if bt_match:
            extracted['bluetooth_version'] = float(bt_match.group(1))
            self.stats['features_extracted'] += 1
        
        # Extract driver size
        driver_match = re.search(self.EXTRACTION_PATTERNS['driver_size'], text_lower, re.IGNORECASE)
        if driver_match:
            extracted['driver_size_mm'] = float(driver_match.group(1))
            self.stats['features_extracted'] += 1
        
        # Extract ANC dB level
        anc_match = re.search(self.EXTRACTION_PATTERNS['anc_db'], text_lower, re.IGNORECASE)
        if anc_match:
            extracted['anc_db'] = int(anc_match.group(1))
            self.stats['features_extracted'] += 1
        
        # Extract mic count
        mic_match = re.search(self.EXTRACTION_PATTERNS['mic_count'], text_lower, re.IGNORECASE)
        if mic_match:
            extracted['mic_count'] = int(mic_match.group(1))
            self.stats['features_extracted'] += 1
        
        # Extract IPX rating
        ipx_match = re.search(self.EXTRACTION_PATTERNS['ipx_rating'], text_lower, re.IGNORECASE)
        if ipx_match:
            extracted['ipx_rating'] = f"IPX{ipx_match.group(1)}"
            self.stats['features_extracted'] += 1
        
        # Detect noise cancellation
        if any(keyword in text_lower for keyword in ['anc', 'active noise', 'noise cancelling', 'noise cancellation']):
            extracted['has_noise_cancellation'] = 1
        else:
            extracted['has_noise_cancellation'] = 0
        
        # Detect form factor
        if any(keyword in text_lower for keyword in ['tws', 'true wireless', 'earbuds', 'ear buds']):
            extracted['category'] = 'true wireless earbuds'
        elif any(keyword in text_lower for keyword in ['over ear', 'over-ear', 'headphone']):
            extracted['category'] = 'over-ear headphone'
        elif any(keyword in text_lower for keyword in ['neckband', 'neck band']):
            extracted['category'] = 'neckband'
        else:
            extracted['category'] = 'unknown'
        
        return extracted
    
    def normalize_units(self, value: str, field: str) -> Optional[float]:
        """
        Normalize various unit formats to standard units
        
        Args:
            value: Value string to normalize
            field: Field type (battery_life, bluetooth_version, etc.)
            
        Returns:
            Normalized float value
        """
        if not value or pd.isna(value):
            return None
        
        value_str = str(value).lower().strip()
        
        try:
            if field == 'battery_life':
                # Convert various battery formats to hours
                if 'min' in value_str:
                    # Convert minutes to hours
                    minutes = float(re.search(r'(\d+)', value_str).group(1))
                    normalized = minutes / 60.0
                elif any(unit in value_str for unit in ['h', 'hr', 'hour']):
                    # Extract hours
                    normalized = float(re.search(r'(\d+)', value_str).group(1))
                else:
                    # Assume it's already in hours
                    normalized = float(value_str)
                
                self.stats['normalization_applied'] += 1
                return normalized
            
            elif field == 'bluetooth_version':
                # Extract version number (e.g., "5.3" from "Bluetooth v5.3")
                match = re.search(r'([0-9]\.[0-9])', value_str)
                if match:
                    normalized = float(match.group(1))
                    self.stats['normalization_applied'] += 1
                    return normalized
                return None
            
            elif field == 'driver_size':
                # Convert to mm
                if 'cm' in value_str:
                    cm = float(re.search(r'(\d+\.?\d*)', value_str).group(1))
                    normalized = cm * 10  # cm to mm
                elif 'mm' in value_str:
                    normalized = float(re.search(r'(\d+\.?\d*)', value_str).group(1))
                else:
                    normalized = float(value_str)
                
                self.stats['normalization_applied'] += 1
                return normalized
            
            elif field == 'price':
                # Remove currency symbols and commas
                cleaned = re.sub(r'[₹,\s]', '', value_str)
                normalized = float(cleaned)
                self.stats['normalization_applied'] += 1
                return normalized
            
            else:
                # Try to convert to float directly
                return float(value_str)
        
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not normalize {field}: {value} - {e}")
            return None
    
    def enhance_dataset(self, input_file: str, output_file: str) -> pd.DataFrame:
        """
        Enhance existing dataset by extracting additional features from product names
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to save enhanced CSV file
            
        Returns:
            Enhanced DataFrame
        """
        logger.info(f"Loading dataset from {input_file}")
        df = pd.read_csv(input_file)
        
        initial_count = len(df)
        logger.info(f"Processing {initial_count} records...")
        
        # Extract features from product names
        enhanced_features = []
        for idx, row in df.iterrows():
            product_name = row.get('product_name', '') or row.get('name', '')
            
            # Extract features using prompt engineering
            features = self.extract_with_prompt_engineering(product_name)
            enhanced_features.append(features)
            
            self.stats['total_processed'] += 1
            
            if (idx + 1) % 50 == 0:
                logger.info(f"Processed {idx + 1}/{initial_count} records...")
        
        # Convert to DataFrame and merge with original
        features_df = pd.DataFrame(enhanced_features)
        
        # Merge extracted features with original data (don't overwrite existing values)
        for col in features_df.columns:
            if col not in df.columns:
                df[col] = features_df[col]
            else:
                # Fill missing values only
                df[col] = df[col].fillna(features_df[col])
        
        # Apply normalization to existing columns
        if 'battery_life_hrs' in df.columns:
            df['battery_life_hrs'] = df['battery_life_hrs'].apply(
                lambda x: self.normalize_units(x, 'battery_life') if pd.notna(x) else x
            )
        
        if 'bluetooth_version' in df.columns:
            df['bluetooth_version'] = df['bluetooth_version'].apply(
                lambda x: self.normalize_units(x, 'bluetooth_version') if pd.notna(x) else x
            )
        
        if 'driver_size_mm' in df.columns:
            df['driver_size_mm'] = df['driver_size_mm'].apply(
                lambda x: self.normalize_units(x, 'driver_size') if pd.notna(x) else x
            )
        
        if 'price_inr' in df.columns:
            df['price_inr'] = df['price_inr'].apply(
                lambda x: self.normalize_units(x, 'price') if pd.notna(x) else x
            )
        
        # Add metadata
        df['enhanced_at'] = datetime.now().isoformat()
        
        # Save enhanced dataset
        df.to_csv(output_file, index=False)
        logger.info(f"Enhanced dataset saved to {output_file}")
        
        # Print statistics
        self.print_stats(df)
        
        return df
    
    def print_stats(self, df: pd.DataFrame):
        """Print enhancement statistics"""
        logger.info("\n" + "="*60)
        logger.info("ENHANCEMENT STATISTICS")
        logger.info("="*60)
        logger.info(f"Total records processed: {self.stats['total_processed']}")
        logger.info(f"Features extracted: {self.stats['features_extracted']}")
        logger.info(f"Normalizations applied: {self.stats['normalization_applied']}")
        logger.info(f"\nDataset completeness:")
        
        key_columns = ['battery_life_hrs', 'bluetooth_version', 'driver_size_mm', 
                      'has_noise_cancellation', 'category', 'price_inr', 'rating']
        
        for col in key_columns:
            if col in df.columns:
                completeness = (df[col].notna().sum() / len(df)) * 100
                logger.info(f"  {col}: {completeness:.1f}% complete")
        
        logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    scraper = EnhancedScraper()
    
    # Enhance the combined dataset
    enhanced_df = scraper.enhance_dataset(
        input_file='data/combined-headphones-dataset.csv',
        output_file='data/enhanced-headphones-dataset.csv'
    )
    
    logger.info(f"✓ Enhancement complete! Enhanced dataset has {len(enhanced_df)} records")
    logger.info(f"✓ Output saved to: data/enhanced-headphones-dataset.csv")


if __name__ == "__main__":
    main()
