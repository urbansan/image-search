"""TODO: This file is uncompleted work kept for future development.
Couldn't be finalized because of network issues and large size of torchvision and torch pretrained models"""

# from io import BytesIO
#
# import numpy as np
# import torch
# import torch.nn as nn
# import torchvision.models as models
# import torchvision.transforms as transforms
# from image_search.common.vector_and_cache import get_redis
# from PIL import Image
#
# # Connect to Redis
#
# # Define image transformation and model for feature extraction
# transform = transforms.Compose(
#     [
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
#     ]
# )
#
# model = models.resnet18(pretrained=True)
# model = nn.Sequential(*list(model.children())[:-1])
# model.eval()
#
#
# def extract_features(image_data: bytes):
#     with BytesIO(image_data) as img_io:
#         image = Image.open(img_io).convert("RGB")
#         image = transform(image).unsqueeze(0)
#         with torch.no_grad():
#             features = model(image).numpy().flatten()
#         return features
#
#
# async def index_image(image_id, image_data: bytes):
#     redis_client = get_redis()
#     features = extract_features(image_data).astype(np.float32).tobytes()
#     await redis_client.hset(image_id, mapping={"vec": features})
#
#
# async def search_similar_images(query_image_path, top_k: int = 5):
#     redis_client = get_redis()
#     query_features = extract_features(query_image_path).astype(np.float32).tobytes()
#
#     return await redis_client.execute_command(
#         "FT.SEARCH",
#         "idx",
#         "*=>[KNN $top_k @vec $query_vec AS score]",
#         "PARAMS",
#         "2",
#         "query_vec",
#         query_features,
#         "top_k",
#         top_k,
#         "SORTBY",
#         "score",
#         "ASC",
#         "RETURN",
#         "1",
#         "vec",
#         "DIALECT",
#         "2",
#     )
#
#
# async def create_redis_index():
#     redis = get_redis()
#     await redis.execute_command(
#         "FT.CREATE",
#         "idx",
#         "ON",
#         "HASH",
#         "SCHEMA",
#         "vec",
#         "VECTOR",
#         "FLAT",
#         "6",
#         "TYPE",
#         "FLOAT32",
#         "DIM",
#         "512",
#         "DISTANCE_METRIC",
#         "COSINE",
#     )
#
#
# # # Index example images
# # index_image("image1", "path/to/image1.jpg")
# # index_image("image2", "path/to/image2.jpg")
