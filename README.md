# RWKV-15PUZZLE

A specialized RWKV model for solving 15-puzzle problems

![demo](./assets/demo.gif)

## Requirements

- rwkv
- tkinter

## Quick Start

- Run `demo.py` or `minimum_inference.py`

## Model

The current model `rwkv_15puzzle_20241214.pth` is a specialized RWKV-v6 model trained on 1m 15-puzzle samples (~2.1B tokens) specifically for solving 15-puzzle problems.

Model specifications:
- Parameters: ~4M
- Vocabulary size: 83
- Architecture: 4 layers, 256 dimensions

The model includes a simple improvement for better performance (see `model.py` line 372). Corresponding modifications were made in the inference code (`rwkv_model.py` lines 852, 893-896).

## Training

The model was trained using the [RWKV-LM](https://github.com/BlinkDL/RWKV-LM) repository.

Hyperparameters:
- `M_BSZ`: 64
- `CTX_LEN`: 8192
- `LR`: 12e-4 to 3e-5
- `ADAM_EPS`: 1e-18
- `ADAM_BETA1`: 0.9
- `ADAM_BETA2`: 0.999
- `WEIGHT_DECAY`: 0.1

![Training Loss Curve](./assets/loss.png)
