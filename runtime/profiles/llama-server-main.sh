#!/usr/bin/env bash
llama-server \
  --model models/qwen2.5-7b-instruct-q4_k_m.gguf \
  --ctx-size 4096 \
  --n-gpu-layers 20 \
  --n-threads 8 \
  --port 8081
