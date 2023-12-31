#
# Created on Mon Nov 27 2023 20:37:03
# Author: Mukai (Tom Notch) Yu
# Email: myual@connect.ust.hk
# Affiliation: Hong Kong University of Science and Technology
#
# Copyright Ⓒ 2023 Mukai (Tom Notch) Yu
#
import os
import sys
from abc import ABC
from abc import abstractclassmethod

import cv2
import numpy as np
import torch

# Calculate the relative path to the project root
project_root = os.path.join(os.path.dirname(__file__), "..")
project_root = os.path.normpath(project_root)  # Normalize the path
# Add the project root to sys.path
sys.path.append(project_root)

from models.superpoint import SuperPoint


class FeatureExtractor(ABC):
    def __new__(
        cls, config, device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ):
        # Use __new__ to create an instance of the appropriate subclass
        if config["extractor"] is None:
            raise ValueError("Missing extractor config")

        if config["extractor"] == "SIFT":
            return super(FeatureExtractor, cls).__new__(SiftExtractor)
        elif config["extractor"] == "Superpoint":
            return super(FeatureExtractor, cls).__new__(SuperpointExtractor)
        else:
            raise ValueError(
                "Unsupported feature extractor type "
                + config["extractor"]
                + " in config"
            )

    def __init__(
        self,
        config,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    ):
        # This will only be called if a subclass instance is not created in __new__
        # Initialize shared configuration parameters
        self.config = config
        self.max_keypoints = int(config["max_keypoints"])
        self.descriptor_dim = int(config["descriptor_dim"])

        self.device = device

    @abstractclassmethod
    def __call__(self, image):
        # This will be called when the instance is called like a function, e.g.
        # feature_extractor = FeatureExtractor(config["feature_extraction"])
        # features = feature_extractor(image)
        pass


class SiftExtractor(FeatureExtractor):
    def __init__(
        self,
        config,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    ):
        super().__init__(config)
        self.contrast_threshold = float(config["SIFT"]["contrast_threshold"])
        self.edge_threshold = float(config["SIFT"]["edge_threshold"])
        self.sigma = float(config["SIFT"]["sigma"])

        self.sift = cv2.SIFT_create(
            nfeatures=self.max_keypoints,
            contrastThreshold=self.contrast_threshold,
            edgeThreshold=self.edge_threshold,
            sigma=self.sigma,
        )

    def __call__(self, image):
        keypoints, descriptors = self.sift.detectAndCompute(image, None)
        keypoints, descriptors = (
            keypoints[: self.max_keypoints],
            descriptors[: self.max_keypoints],
        )  # have to cap it since cv2 is dumb sb
        confidence_scores = torch.tensor([k.response for k in keypoints]).unsqueeze(-1)
        keypoints = torch.tensor([(kp.pt[0], kp.pt[1]) for kp in keypoints])
        descriptors = torch.tensor(descriptors)
        return keypoints, descriptors, confidence_scores


class SuperpointExtractor(FeatureExtractor):
    def __init__(
        self,
        config,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    ):
        super().__init__(config)
        self.superpoint_config = config["Superpoint"]
        self.superpoint_config["max_keypoints"] = self.max_keypoints
        self.superpoint_config["descriptor_dim"] = self.descriptor_dim
        self.superpoint_config["nms_radius"] = int(self.superpoint_config["nms_radius"])

        self.superpoint = SuperPoint(self.superpoint_config).eval().to(self.device)

    def __call__(self, image):
        # Convert the input image to a torch tensor
        input_tensor = (
            torch.from_numpy(image / 255.0).float()[None, None].to(self.device)
        )

        # Pass the image through the SuperPoint model
        result = self.superpoint(input_tensor)
        return (
            result["keypoints"][0].to("cpu"),
            result["descriptors"][0].T.to("cpu"),
            result["scores"][0][:, np.newaxis].to("cpu"),
        )
