"""
Test script for FRED Cloud Function
Run locally to verify functionality before deployment
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fred.extractor import FREDExtractor
from fred.transformer import FREDTransformer
from common.config import config

def test_extractor():
    """Test FRED data extraction"""
    print("=" * 60)
    print("Testing FRED Extractor")
    print("=" * 60)

    extractor = FREDExtractor()

    # Test single series
    print("\n1. Fetching DGS10 (US 10Y Treasury)...")
    try:
        data = extractor.fetch_series("DGS10", start_date="2024-01-01", end_date="2024-01-31")
        print(f"✓ Fetched {len(data['observations'])} observations")
        print(f"  Sample: {data['observations'][:2]}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

    extractor.close()
    return True

def test_transformer():
    """Test data transformation"""
    print("\n" + "=" * 60)
    print("Testing FRED Transformer")
    print("=" * 60)

    transformer = FREDTransformer()

    # Mock series data
    mock_data = {
        "series_id": "DGS10",
        "observations": [
            {"date": "2024-01-02", "value": "4.05"},
            {"date": "2024-01-03", "value": "4.10"},
            {"date": "2024-01-04", "value": "."}  # Missing value
        ]
    }

    print("\n1. Transforming observations...")
    try:
        transformed = transformer.transform_observations(mock_data, "test-run-123")
        print(f"✓ Transformed {len(transformed)} observations (1 missing value filtered)")
        print(f"  Sample: {json.dumps(transformed[0], indent=2, default=str)}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

    return True

def test_full_pipeline():
    """Test full extraction and transformation pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline")
    print("=" * 60)

    extractor = FREDExtractor()
    transformer = FREDTransformer()

    series_list = ["DGS2", "DGS10", "EURUSD"]

    print(f"\n1. Processing {len(series_list)} series...")

    for series_id in series_list:
        try:
            # Extract
            print(f"\n  Processing {series_id}...")
            data = extractor.fetch_series(series_id, start_date="2024-02-01", end_date="2024-02-10")

            # Transform
            observations = transformer.transform_observations(data, "test-run-456")

            print(f"  ✓ {series_id}: {len(observations)} observations")

        except Exception as e:
            print(f"  ✗ {series_id}: {str(e)}")

    extractor.close()
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FRED Cloud Function Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Project: {config.GCP_PROJECT_ID}")
    print(f"FRED API Key: {'✓ Set' if config.FRED_API_KEY else '✗ Not Set'}")

    if not config.FRED_API_KEY:
        print("\n⚠ FRED_API_KEY not set. Please set environment variable.")
        print("  export FRED_API_KEY=your_key_here")
        return

    # Run tests
    tests = [
        ("Extractor", test_extractor),
        ("Transformer", test_transformer),
        ("Full Pipeline", test_full_pipeline)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Ready for deployment.")
    else:
        print("\n⚠ Some tests failed. Please fix before deployment.")

if __name__ == "__main__":
    main()
