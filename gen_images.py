import argparse

from datetime import datetime
import os
import shutil
from pathlib import Path

from re_edge_gpt import ImageGen, ImageGenAsync

from blog_writer.agents.image_generator import ImageGeneratorAgent
from blog_writer.config.config import load_config
from blog_writer.config.definitions import ROOT_DIR
from blog_writer.config.logger import logger

# create a temporary output directory for testing purposes
test_output_dir = f"images/custom/{datetime.now().strftime('%Y%m%d%H%M%S')}"
auth_cooker = open(f"{ROOT_DIR}/data/bing_cookies.json", "r+").read()
sync_gen = ImageGen(auth_cookie=auth_cooker)
async_gen = ImageGenAsync(auth_cookie=auth_cooker)


# Generate image list sync
def generate_image_sync(name, description):
    image_list = sync_gen.get_images(description)
    print(image_list)
    for i, image_url in enumerate(image_list):
        sync_gen.save_images([image_url], test_output_dir, file_name=f"{name}_{i}")


if __name__ == "__main__":
    if not os.path.exists(test_output_dir):
        os.makedirs(test_output_dir)
    # Make dir to save image
    Path(test_output_dir).mkdir(exist_ok=True)

    # read from -c
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("-c", "--content", type=str, help="Content")
    args = parser.parse_args()

    # Generate image sync
    article_content = args.content
    if article_content is None:
        raise Exception("Content is required")
    desc = f"Create image about this description:\n{article_content}"
    config = load_config()
    logger.info("Start generate image")
    image_generate_agent = ImageGeneratorAgent(
        model_config=config.model_config_ollama,
    )
    image_generate_agent.run(desc, test_output_dir)
    logger.info("Gen image done")
