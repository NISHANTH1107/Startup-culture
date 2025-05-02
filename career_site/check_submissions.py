#!/usr/bin/env python
import time
import os
import sys
from career_site import scoring_logic
import traceback

# Add the project path to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def check_forms():
    """Check for new form submissions"""
    try:
        print(f"Checking forms at {scoring_logic.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return scoring_logic.process_single_submission()
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run checks every 60 seconds for the duration of one hour"""
    print(f"Starting hourly check routine at {scoring_logic.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(BASE_DIR, "career_site", "generated_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Run for 60 minutes (3600 seconds)
    end_time = time.time() + 3540  # Run for 59 minutes to ensure we complete before next task
    
    while time.time() < end_time:
        result = check_forms()
        if result:
            print("Successfully processed submission!")
        else:
            print("No new submissions to process.")
        
        # Sleep for 60 seconds before checking again
        print(f"Sleeping for 60 seconds until next check...")
        time.sleep(60)
    
    print(f"Completed hourly check routine at {scoring_logic.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()