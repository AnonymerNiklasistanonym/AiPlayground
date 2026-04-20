# llama.cpp

An easy way to run lots of trained neural net models (for example from [huggingface.co](https://huggingface.co)) locally.

## Build

```sh
# Only necessary once
git clone https://github.com/ggml-org/llama.cpp.git --depth 1 --single-branch
# Repeat every time there are changes
cd llama.cpp
git pull
cmake -B build -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON -DLLAMA_BUILD_TESTS=OFF
cmake --build build -j --config Release
```

**CUDA**: Add `-DGGML_CUDA=ON`

**VULKAN**: Add `-DGGML_VULKAN=ON`

## Run

Good models (04.2026):

| Name | Version | Size | Speed CPU | Speed CUDA GPU (RTX 3060TI) |
| --- | --- | --- | --- | --- |
| [unsloth/gemma-4-E4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF) | [`UD-Q3_K_XL`](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF?show_file_info=gemma-4-E4B-it-UD-Q3_K_XL.gguf) | 4.56 GB | 12 Tk/s | 60 Tk/s |

### Terminal

```sh
./build/bin/llama-cli -hf $MODEL:$VERSION
# Example
./build/bin/llama-cli -hf unsloth/gemma-4-E4B-it-GGUF:UD-Q4_K_XL
```

### Web Interface

```sh
./build/bin/llama-server -hf $MODEL:$VERSION
# Example
./build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:UD-Q4_K_XL
```

## Apps

### Demo

Simple demo of how to do a basic chat completion:

```sh
# Terminal 1
./llama.cpp/build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:UD-Q3_K_XL
# Terminal 2
uv run app_demo.py -m unsloth/gemma-4-E4B-it-UD-Q3_K_XL "what is the capital of germany"
# The capital of Germany is Berlin.

uv run app_demo.py -m unsloth/gemma-4-E4B-it-UD-Q3_K_XL --system="Always respond with WTH?" "what is the capital of germany"
# WTH?
```

### Demo with Tools

```sh
# Terminal 1
./llama.cpp/build/bin/llama-server -hf unsloth/gemma-4-E4B-it-GGUF:UD-Q3_K_XL
# Terminal 2
uv run app_tools_demo.py -m unsloth/gemma-4-E4B-it-UD-Q3_K_XL "reverse the word 'hello'"
# [iter 0] tool call: tool_reverse_text({"text":"hello"})
# The reversed word is 'olleh'.

uv run app_tools_demo.py -m unsloth/gemma-4-E4B-it-UD-Q3_K_XL "create a shopping todo file with the elements buy milk, cheese and eggs and mark bread as already bought"
# [iter 0] tool call: tool_write_markdown_todo_file({"text":"# TODOs\n- [ ] buy milk\n- [ ] buy cheese\n- [ ] buy eggs\n- [x] bread"})
# The shopping todo file has been created.

uv run app_tools_demo.py -m unsloth/gemma-4-E4B-it-UD-Q3_K_XL "read the markdown todo file and update the list inside by crossing the item milk"
# [iter 0] tool call: tool_read_markdown_todo_file({"text":"markdown todo file"})
# [iter 1] tool call: tool_write_markdown_todo_file({"text":"# TODOs\n- [x] buy milk\n- [ ] buy cheese\n- [ ] buy eggs\n- [x] bread"})
# The item "buy milk" has been marked as complete in the markdown todo file.
```

The first call creates `todos.md`:

```md
# TODOs
- [ ] buy milk
- [ ] buy cheese
- [ ] buy eggs
- [x] bread
```

The second call updates `todos.md`:

```md
# TODOs
- [x] buy milk
- [ ] buy cheese
- [ ] buy eggs
- [x] bread
```
