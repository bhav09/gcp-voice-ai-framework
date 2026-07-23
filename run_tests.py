import sys
import os
import pytest
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VoiceFrameworkTestRunner")

def run_all_tests():
    logger.info("======================================================================")
    logger.info(" STARTING MASTER TEST SUITE FOR UNIVERSAL GCP VOICE AI FRAMEWORK ")
    logger.info(" Target GCP Project: gen-demo-66-20250711 ")
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
