"""
Test runner for all unit tests
Run this file to execute all test suites and generate HTML report
"""
import subprocess
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all test suites and generate HTML report"""
    
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'test-reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = os.path.join(reports_dir, f'test_report_{timestamp}.html')
    latest_report = os.path.join(reports_dir, 'test_report_latest.html')
    
    print("="*70)
    print("BTC TRADING BOT - TEST SUITE")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Report will be saved to: {html_report}")
    print("="*70)
    print()
    
    # Run pytest with HTML report generation
    cmd = [
        'pytest',
        'tests/',
        '-v',
        '--tb=short',
        f'--html={html_report}',
        '--self-contained-html',
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term',
        '--junit-xml=' + os.path.join(reports_dir, f'junit_{timestamp}.xml')
        # NO SKIP - All tests must run and pass
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        
        # Copy to latest
        if os.path.exists(html_report):
            import shutil
            shutil.copy2(html_report, latest_report)
        
        print()
        print("="*70)
        print("TEST EXECUTION COMPLETE")
        print("="*70)
        print(f"✅ HTML Report: {html_report}")
        print(f"✅ Latest Report: {latest_report}")
        print(f"✅ Coverage Report: htmlcov/index.html")
        print(f"✅ JUnit XML: {os.path.join(reports_dir, f'junit_{timestamp}.xml')}")
        print("="*70)
        
        return result.returncode
        
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
