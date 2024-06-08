import os
from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file

if __name__ == "__main__":
    problem = read_file("input.txt")
    subject = f'Write a blog about\n\"\"\"{problem}\n\"\"\"'
    use_last_folder = input("Use last folder? (y/n): ")
    load_from = ""
    
    if use_last_folder == "y":
        # load_from = "240513091635_guide-to-database-partitioning-types-and-benefits"
        # list all folder of directory
        folders = os.listdir(".working_space")
        folders = [folder for folder in folders if folder[0].isdigit()]
        
        # sort by name
        folders.sort()
        
        # get the last folder
        last_folder = folders[-1]
        print(f"Last folder: {last_folder}")
        load_from = last_folder
        
    generate(subject, load_from)
