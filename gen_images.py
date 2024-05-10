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
    Design Concept: The banner could be a combination of elements that represent Datadog, Node.js, and the concept of navigating pitfalls.

Datadog Representation: You could use the Datadog logo or a stylized version of it. You could also use an image of a dog as a playful nod to the name.
Node.js Representation: Incorporate the Node.js logo or some recognizable aspect of it into the design.
Navigating Pitfalls: To represent the concept of navigating pitfalls, you could use imagery like warning signs, hurdles, or a maze. Another idea could be a path that starts with the Node.js logo, goes through a field of warning signs or hurdles (representing the pitfalls), and ends at the Datadog logo.
Color Scheme: Use a color scheme that aligns with the Datadog and Node.js brand colors to maintain consistency.
Typography: The title of your blog post should be clearly readable. You could use bold, large letters and place it either at the top or center of the banner.
    """
    desc = f"Create image about this description:\n{article_content}"
    curTime = datetime.now().strftime("%Y%m%d%H%M%S")
    test_generate_image_sync(curTime,desc)