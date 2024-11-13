import os

os.environ["RWKV_JIT_ON"] = "1"
os.environ["RWKV_CUDA_ON"] = "0"

from rwkv_model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS
from rwkv.rwkv_tokenizer import TRIE_TOKENIZER

model = RWKV(model="rwkv-final.pth", strategy="cuda fp16", verbose=False)
pipeline = PIPELINE(model, "rwkv_vocab_v20230424")
pipeline.tokenizer = TRIE_TOKENIZER("puzzle15_vocab.txt")
gen_args = PIPELINE_ARGS(top_k=1, alpha_frequency=0, alpha_presence=0, token_stop=[59])

input_str = """<input>
<board>
15 0  2  12 
14 7  11 8  
1  5  3  4  
6  13 10 9  
</board>
</input>
"""

print(f'{" Model input ":-^100}\n{input_str}\n{" Model output ":-^100}')
solution = pipeline.generate(input_str, token_count=500000, args=gen_args, callback=lambda x: print(x, end="", flush=True))

# check if the solution is correct
from tools import is_solution

puzzle = input_str[16:-18].strip().replace("\n", " ")
puzzle = [int(x) for x in puzzle.split()]
puzzle = [puzzle[i : i + 4] for i in range(0, 16, 4)]
solution = solution.split("<output>")[-1].strip().split(" ")
corrcet = is_solution(puzzle, solution)
print("-" * 100)
print(f"Correct (Python check): {corrcet}")
