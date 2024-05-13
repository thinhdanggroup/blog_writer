from blog_writer.core.generate import generate
from blog_writer.utils.file import read_file

if __name__ == "__main__":
    problem = read_file("input.txt")
    subject = f'Write a blog about\n\"\"\"{problem}\n\"\"\"'
    load_from = ""
    load_from = "240513091635_guide-to-database-partitioning-types-and-benefits"
    generate(subject, load_from)
