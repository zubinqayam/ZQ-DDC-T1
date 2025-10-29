#!/usr/bin/env python3
import os, sys
for k in ["ZQ_DDC_FAVICON"]:
    if k not in os.environ:
        print(f"WARN: {k} not set; using default")
print("Environment looks OK for Core V1.")
sys.exit(0)
