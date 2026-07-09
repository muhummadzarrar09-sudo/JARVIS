#!/usr/bin/env bash
# Auto-generated BRAVO-1 runtime profile
llama-server \
  --model models/qwen2.5-7b-instruct-q4_k_m.gguf \
  --ctx-size 8192 \
  --n-gpu-layers 32 \
  --n-threads 10 \
  --port 8081
