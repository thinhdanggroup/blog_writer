from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file

if __name__ == "__main__":
    problem = read_file("input.txt")
    subject = f'Write a blog about\n\"\"\"{problem}\n\"\"\"'
    load_from = "240304212621_--creating_a_blog_th"
    generate(subject, load_from)
