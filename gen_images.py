from datetime import datetime
import os
import shutil
from pathlib import Path

from re_edge_gpt import ImageGen, ImageGenAsync

# create a temporary output directory for testing purposes
test_output_dir = ".working_space/0_image"
auth_cooker = open("data/bing_cookies.txt", "r+").read()
sync_gen = ImageGen(auth_cookie=auth_cooker)
async_gen = ImageGenAsync(auth_cookie=auth_cooker)


# Generate image list sync
def test_generate_image_sync(name, desc):
    image_list = sync_gen.get_images(desc)
    print(image_list)
    for i, image_url in enumerate(image_list):
        sync_gen.save_images([image_url], test_output_dir, file_name=f"{name}_{i}")

if __name__ == "__main__":
    # Make dir to save image
    Path(test_output_dir).mkdir(exist_ok=True)

    # Generate image sync
    article_content = """
    Design Concept:This article provides a step-by-step guide on how to implement user tracking in NestJS applications using DataDog. It covers the basics of NestJS and DataDog, explains the concept of interceptors in NestJS, and shows how to create a custom UserTrackingInterceptor to track user behavior. The guide also covers how to apply and configure the interceptor, test its functionality, and view the tracking data in DataDog. By the end of this article, you will have a comprehensive understanding of user tracking and be able to implement it in your own NestJS applications.
    """
    desc = f"Create image about this description:\n{article_content}"
    curTime = datetime.now().strftime("%Y%m%d%H%M%S")
    test_generate_image_sync(curTime,desc)