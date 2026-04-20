# latex_proofreader

## Run

```sh
# Terminal 1
./llama.cpp/build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:UD-Q3_K_XL
# Terminal 2
uv run latex_proofreader.py -m unsloth/gemma-4-E4B-it-GGUF:UD-Q3_K_XL path/to/latex_project check
```
