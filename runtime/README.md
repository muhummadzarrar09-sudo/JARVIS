# runtime

Local runtime layer for BRAVO-1.

## Initial role
- document local llama.cpp / llama-server profiles
- hold runtime startup scripts
- keep model serving separate from operator logic

## Immediate target
- fast lane: small GGUF instruct model
- main lane: larger GGUF instruct model
- host: local only

## Profile templates
- `profiles/templates/llama-server-low.txt`
- `profiles/templates/llama-server-medium.txt`
- `profiles/templates/llama-server-heavy.txt`
