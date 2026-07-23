import sys
import os
import pytest
import logging

# Load environment variables from local .env if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VoiceFrameworkTestRunner")

def run_all_tests():
    project_id = os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
    logger.info("======================================================================")
    logger.info(" STARTING MASTER TEST SUITE FOR UNIVERSAL GCP VOICE AI FRAMEWORK ")
    logger.info(f" Target GCP Project: {project_id} ")
    logger.info("======================================================================")

    template_dir = os.path.dirname(os.path.abspath(__file__))
    test_dirs = [
        os.path.join(template_dir, "tests/unit"),
        os.path.join(template_dir, "tests/integration"),
        os.path.join(template_dir, "tests/synthetic_scenarios"),
        os.path.join(template_dir, "tests/evaluations")
    ]

    exit_code = pytest.main(["-v", "-s"] + test_dirs)
    
    if exit_code == 0:
        logger.info("✅ ALL TEST SUITES PASSED SUCCESSFULLY!")
    else:
        logger.error(f"❌ TEST SUITE FAILED WITH EXIT CODE: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_all_tests())
