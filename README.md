# COMP 5222 Final Project - Group 10 - GNN For Feature Matching

## Usage

### 1. Environment Setup

```Shell
conda env create -f environment.yml
conda activate gnn-feature-matching
```

### 2. Download Data

Download the COCO2014 dataset files for training

```Shell
wget http://images.cocodataset.org/zips/train2014.zip
```

Download the validation set

```Shell
wget http://images.cocodataset.org/zips/val2014.zip
```

Download the test set

```Shell
wget http://images.cocodataset.org/zips/test2014.zip
```

### 3. Training Directions

To train the SuperGlue with default parameters, run the following command:

```shell
./train_<model_name>.sh
```

### 4. Testing Directions

```shell
./test_<model_name>.sh
```

### 5. Additional useful command line parameters

- Use `--epoch` to set the number of epochs (default: `20`).
- Use `--train_path` to set the path to the directory of training images.
- Use `--eval_output_dir` to set the path to the directory in which the visualizations is written (default: `dump_match_pairs/`).
- Use `--show_keypoints` to visualize the detected keypoints (default: `False`).
- Use `--viz_extension` to set the visualization file extension (default: `png`). Use pdf for highest-quality.

### 6. Visualization Demo

The matches are colored by their predicted confidence in a jet colormap (Red: more confident, Blue: less confident).

You should see images like this inside of `dump_match_pairs/`

<img src="assets/8349_matches.png" width="800">
<img src="assets/4599_matches2.png" width="800">
<img src="assets/2799_matches.png" width="800">
<img src="assets/3849_matches2.png" width="800">
<img src="assets/3949_matches.png" width="800">

## Task Introduction

In many tasks of computer vision, matching discrete features/objects across different frames is a difficult combinatorial optimization problem which is NP-complete, and is usually relaxed as an optimal transport problem.
Specifically in SLAM, core of self-driving vehicles, feature matching is involved as a pivotal middle-end, it inputs two sets of sparse feature points extracted from a pair of images, which are captured from stereo cameras or temporally adjacent frames of a monocular camera, and outputs a bijection function of the features according to their actual physical 3D point. The feature descriptor is a 1D vector encoding of its appearance.
Traditionally, it was often approached by hand-crafted feature extraction such as SIFT, and Hungarian algorithm for feature matching. However, since the hand-crafted feature as well as the similarity measurements between a pair of features are based on limited heuristics, the matching results are often suboptimal.

For more detailed information on the task, please refer to the [SuperGlue paper presentation slide](https://hkustconnect-my.sharepoint.com/:p:/g/personal/myual_connect_ust_hk/EfeHMWLXjgZDlcu-Ah43hC4B7sI5Okl_BFJ5LFrXEN0SJg?e=UzQDQy)

## Existing Work

1. SuperGlue[[1]](#1):
   SuperGlue is built upon the feature extractor SuperPoint. Given the key point features and their descriptors extracted from two frames, SuperGlue creates inter-image and intra-image graphs by constructing a fully connected graph between all the features in their respective relations. It then passes the graphs to a GNN with attentional aggregation, alternatingly running inter-image attention and intra-image attention for multiple layers. Eventually, the GNN produces the matching scores for all pairs of nodes. It then applies the Sinkhorn algorithm (a differentiable version of the Hungarian Algorithm) to solve for the bijection function.

1. Follow-up work: SGMNet[[2]](#2), ClusterGNN[[3]](#3)
   ClusterGNN: Although superglue has achieved good results, its use of fully connected
   graphs results in high time complexity. To solve this problem, ClusterGNN proposed an
   attentional GNN architecture that operates on clusters of features and improves efficiency
   at the same time. Moreover, a coarse-to-fine paradigm is implemented to establish the
   local graphs for feature matching, which enhances the message-passing efficiency.

## Proposed method

In real-world applications, the algorithm is supposed to run in real time on edge computing platforms. However, we observed that the existing works utilize fully connected graphs of the features and aggregate neighbor information alternatingly because of the two types of edges. To alleviate these problems, we propose to:

1. Use node and edge pooling to reduce the graph scale in intermediate layers and recover
   the scale in the final output.

1. Merge the inter-image graphs and intra-image graphs into one by labeling the two types of edges, so that the two aggregation schemes can be carried out simultaneously to reduce the number of layers and simplify the implementation.

## Team Member

- WANG, Yicheng <ywangmy@connect.ust.hk>
- YANG, Lin <lyangbe@connect.ust.hk>
- YU, Mukai <myual@connect.ust.hk>

## References

<a id="1">[1]</a> Y. Shi, J.-X. Cai, Y. Shavit, T.-J. Mu, W. Feng, and K. Zhang, “ClusterGNN: Cluster-based Coarse-to-Fine Graph Neural Network for Efficient Feature Matching,” in 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), Jun. 2022, pp. 12507–12516. doi: [10.1109/CVPR52688.2022.01219](https://doi.org/10.1109/CVPR52688.2022.01219).

<a id="1">[2]</a> H. Chen et al., “Learning to Match Features with Seeded Graph Matching Network,” in 2021 IEEE/CVF International Conference on Computer Vision (ICCV), Oct. 2021, pp. 6281–6290. doi: [10.1109/ICCV48922.2021.00624](https://doi.org/10.1109/ICCV48922.2021.00624).

<a id="1">[3]</a> P.-E. Sarlin, D. DeTone, T. Malisiewicz, and A. Rabinovich, “SuperGlue: Learning Feature Matching With Graph Neural Networks,” presented at the Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2020, pp. 4938–4947. Accessed: Oct. 07, 2023. [Online]. Available: <https://openaccess.thecvf.com/content_CVPR_2020/html/Sarlin_SuperGlue_Learning_Feature_Matching_With_Graph_Neural_Networks_CVPR_2020_paper.html>
