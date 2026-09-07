"""Manual pipeline runner. Invoke as a module from the repository root."""
import argparse
import json
from dataclasses import asdict
from backend.modules.cv.engine.pipeline import SmartCVPipeline


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='PDF con texto o TXT')
    parser.add_argument('--mode', choices=['local', 'lmstudio'], default='local')
    args = parser.parse_args()
    profile = SmartCVPipeline().process(args.file, args.mode)
    print(json.dumps(asdict(profile), ensure_ascii=False, indent=2))
