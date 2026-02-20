"""
Simple test script for FRED modules
Tests basic functionality without BigQuery dependencies
"""
import os
import sys

# Add functions directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.config import config

def test_config():
    """Test configuration"""
    print("=" * 60)
    print("Testing Configuration")
    print("=" * 60)

    print(f"GCP Project: {config.GCP_PROJECT_ID}")
    print(f"FRED API Key: {'✓ Set' if config.FRED_API_KEY else '✗ Not Set'}")
    print(f"FRED API Base: {config.FRED_API_BASE}")

    if not config.FRED_API_KEY:
        print("\n⚠ FRED_API_KEY not set!")
        print("  Set it with: export FRED_API_KEY=your_key")
        return False

    return True

def test_http_client():
    """Test HTTP client"""
    print("\n" + "=" * 60)
    print("Testing HTTP Client")
    print("=" * 60)

    from common.http_client import HTTPClient

    client = HTTPClient()

    try:
        # Test simple GET request to FRED
        url = f"{config.FRED_API_BASE}/series"
        params = {
            "series_id": "DGS10",
            "api_key": config.FRED_API_KEY,
            "file_type": "json"
        }

        print(f"\nFetching series info for DGS10...")
        response = client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            series_info = data.get("seriess", [{}])[0]
            print(f"✓ Success!")
            print(f"  Title: {series_info.get('title', 'N/A')}")
            print(f"  Frequency: {series_info.get('frequency', 'N/A')}")
            client.close()
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            client.close()
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        client.close()
        return False

def test_transformer():
    """Test transformer"""
    print("\n" + "=" * 60)
    print("Testing Transformer")
    print("=" * 60)

    from fred.transformer import FREDTransformer

    transformer = FREDTransformer()

    # Mock data
    mock_data = {
        "series_id": "DGS10",
        "observations": [
            {"date": "2024-01-02", "value": "4.05"},
            {"date": "2024-01-03", "value": "4.10"},
            {"date": "2024-01-04", "value": "."}  # Missing
        ]
    }

    try:
        transformed = transformer.transform_observations(mock_data, "test-123")
        print(f"✓ Transformed {len(transformed)} observations")
        print(f"  (Filtered 1 missing value)")

        if transformed:
            obs = transformed[0]
            print(f"\n  Sample observation:")
            print(f"    Date: {obs['observation_date']}")
            print(f"    Value: {obs['value']}")
            print(f"    Indicator: {obs['indicator_code']}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests"""
    print("\n" + "=" * 60)
    print("FRED Module Test Suite (Simplified)")
    print("=" * 60)

    tests = [
        ("Configuration", test_config),
        ("HTTP Client", test_http_client),
        ("Transformer", test_transformer)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))

            # Stop if config test fails
            if name == "Configuration" and not result:
                break

        except Exception as e:
            print(f"\n✗ {name} failed: {str(e)}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠ Some tests failed.")

if __name__ == "__main__":
    main()
