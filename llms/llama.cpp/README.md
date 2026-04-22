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

## Clean

### Huggingface

To clean/manage the downloaded huggingface models you can use the tool `hf cache (list|rm <MODEL>)` provided by the Python package `huggingface_hub` (`pacman -S python-huggingface-hub`):

```sh
hf cache list
# ID                                    SIZE LAST_ACCESSED LAST_MODIFIED REFS
# ----------------------------------- ------ ------------- ------------- ----
# model/unsloth/Qwen2.5-Coder-7B-I...   3.0G 5 days ago    5 days ago    main
# model/unsloth/gemma-4-E4B-it-GGUF    46.0G 1 day ago     1 day ago     main
hf cache rm model/unsloth/gemma-4-E4B-it-GGUF
# About to delete 1 repo(s) totalling 46.0G.
#   - model/unsloth/gemma-4-E4B-it-GGUF (entire repo)
# Proceed with deletion? [y/N]: y
# Delete repo: /home/niklas/.cache/huggingface/hub/models--unsloth--gemma-4-E4B-it-GGUF
# Cache deletion done. Saved 46.0G.
# ✓ Deleted 1 repo(s) and 3 revision(s); freed 46.0G.
#   repos_deleted: 1
#   revisions_deleted: 3
#   freed: 46.0G
```

For long model names there is a trick to use the json format to get the ID:

```sh
hf cache list --json | jq | grep -E "\"id|\"size"
#     "id": "model/unsloth/Qwen2.5-Coder-7B-Instruct-128K-GGUF",
#     "size": "3.0G",
hf cache list --json | jq '.[] | {id,size}'
# {
#   "id": "model/unsloth/Qwen2.5-Coder-7B-Instruct-128K-GGUF",
#   "size": "3.0G"
# }
```
