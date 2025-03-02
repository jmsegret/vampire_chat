import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vampire_chat.app.main import main

if __name__ == "__main__":
    main() 