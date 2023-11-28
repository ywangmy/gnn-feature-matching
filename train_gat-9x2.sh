#!/usr/bin/env bash
CUDA_VISIBLE_DEVICES=1 python main.py --mode='train' --model='gat' --match_threshold=0.1 --fraction=0.01 --gnn_layers=9 --show_keypoints --viz --fast_viz --batch_size=12 --learning_rate=1e-4 --graph=2
# 9l 8b = 12556Mb