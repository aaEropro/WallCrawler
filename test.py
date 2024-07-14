from bs4 import BeautifulSoup

# Load your HTML content
with open(r"C:\Users\jovanni\Desktop\electric-angel\text\part0006_split_001.html", 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'lxml')

# Function to transform italic tags to plaintext with asterisks
def transform_italic_tags(soup):
    for tag in soup.find_all(True):  # Find all tags
        if 'class' in tag.attrs and 'italic' in tag['class']:
            tag.replace_with(f"*{tag.get_text()}*")  # Replace with asterisks-wrapped text
        else:
            tag.unwrap()  # Remove the tag but keep its content

# Apply the function to the soup
transform_italic_tags(soup)

# Get the modified HTML
modified_html = str(soup)

# Save the modified HTML to a new file
with open(r"C:\Users\jovanni\Desktop\electric-angel-2\part0005_split_001.html", 'w', encoding='utf-8') as file:
    file.write(modified_html)
