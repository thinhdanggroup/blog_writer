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
    This article is a step-by-step guide to mastering end-to-end testing in NestJS applications using TypeScript. It covers the importance of E2E testing, setting up the testing environment, and writing and running E2E tests. The article also provides unique insights into testing scenarios involving PostgreSQL and Redis databases, including the Cache Aside pattern. Whether you're a beginner or an experienced developer, this article offers valuable knowledge and best practices to ensure the reliability and robustness of your NestJS applications.
    """
    desc = f"Create image about this description:\n{article_content}"
    curTime = datetime.now().strftime("%Y%m%d%H%M%S")
    test_generate_image_sync(curTime, desc)
