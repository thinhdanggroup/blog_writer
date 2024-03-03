from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file

if __name__ == "__main__":
    problem = read_file("input.txt")
    subject = f'Write a blog about\n\"\"\"{problem}\n\"\"\"'
    load_from = "240303123956_write_a_blog_about--"
    generate(subject, load_from)
