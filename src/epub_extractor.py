import zipfile
import os
import xml.etree.ElementTree as ET
from urllib.parse import urljoin


def _loadChapterFiles(epub_path: str) -> list[str]:
    chapter_files = list()

    # Check if the file exists
    if not os.path.exists(epub_path):
        print(f"File {epub_path} does not exist.")
        return

    with zipfile.ZipFile(epub_path, 'r') as epub:
        # Find and open the content.opf file
        opf_file = None
        for file_name in epub.namelist():
            if file_name.endswith('content.opf'):
                opf_file = file_name
                break

        if not opf_file:
            print("content.opf file not found.")
            return

        # Get the base path for resolving chapter files
        opf_dir = os.path.dirname(opf_file)

        # Parse the content.opf file
        with epub.open(opf_file) as f:
            tree = ET.parse(f)
            root = tree.getroot()

            # Define namespaces (check your file's structure if necessary)
            namespaces = {
                'default': 'http://www.idpf.org/2007/opf'
            }

            # Find all the itemrefs that refer to chapters in the spine
            spine = root.find('default:spine', namespaces)
            manifest = {item.get('id'): item.get('href') for item in root.find('default:manifest', namespaces)}

            # Get the list of chapters in reading order
            chapters = [manifest[itemref.get('idref')] for itemref in spine.findall('default:itemref', namespaces)]

            print("Chapter files found:")
            for chapter in chapters:
                chapter_path = os.path.join(opf_dir, chapter)
                chapter_path = chapter_path.replace("\\", "/")  # Ensure correct path format
                print(chapter_path)
                try:
                    with epub.open(chapter_path) as chapter_file:
                        content = chapter_file.read().decode('utf-8')
                        # print(f"\nContent of {chapter_path} (first 500 characters):")
                        # print(content[:500])  # Print the first 500 characters as a preview
                        chapter_files.append(content)
                except KeyError as e:
                    print(f"Could not open {chapter_path}: {e}")

    return chapter_files


import zipfile
import os
import tinycss2

def _italicClasses(epub_path):
    # Check if the file exists
    if not os.path.exists(epub_path):
        print(f"File {epub_path} does not exist.")
        return

    italic_classes = []

    with zipfile.ZipFile(epub_path, 'r') as epub:
        # Find all .css files
        css_files = [file_name for file_name in epub.namelist() if file_name.endswith('.css')]

        if not css_files:
            print("No CSS files found in this EPUB.")
            return

        for css_file in css_files:
            print(f"Processing {css_file}...")
            with epub.open(css_file) as f:
                css_content = f.read().decode('utf-8')
            rules = tinycss2.parse_stylesheet(css_content, skip_whitespace=True)

            italic_selectors = []

            # Iterate over all the rules
            for rule in rules:
                if rule.type == 'qualified-rule':
                    # Extract the selectors and declarations
                    selectors = rule.prelude
                    declarations = rule.content

                    # Check if any declaration contains font-style: italic
                    for declaration in declarations:
                        if (declaration.type == 'declaration' and
                                declaration.name == 'font-style' and
                                declaration.value == 'italic'):
                            # Add the selectors to the results
                            selector_text = ''.join(tinycss2.serialize(s) for s in selectors)
                            italic_selectors.append(selector_text.strip())

    return italic_selectors
    #
    #             # Parse the CSS content
    #             rules = tinycss2.parse_stylesheet(css_content, skip_whitespace=True)
    #
    #             italic_selectors = []
    #
    #             # Iterate over all the rules
    #             for rule in rules:
    #                 if rule.type == 'qualified-rule':
    #                     # Extract the selectors and declarations
    #                     selectors = rule.prelude
    #                     declarations = rule.content
    #
    #                     # Check if any declaration contains font-style: italic
    #                     for declaration in declarations:
    #                         if (declaration.type == 'declaration' and
    #                                 declaration.name == 'font-style' and
    #                                 declaration.value == 'italic'):
    #                             # Add the selectors to the results
    #                             selector_text = ''.join(tinycss2.serialize(s) for s in selectors)
    #                             italic_selectors.append(selector_text.strip())
    #
    # return italic_selectors

                # # Parse the CSS content
                # rules = tinycss2.parse_stylesheet(css_content, skip_whitespace=True)
                #
                # # Look for classes with italic formatting
                # for rule in rules:
                #     if rule.type == 'qualified-rule':
                #         prelude = tinycss2.serialize(rule.prelude).strip()
                #         content = rule.content
                #         class_name = None
                #         for token in rule.prelude:
                #             if token.type == 'ident' and class_name is None:
                #                 class_name = f'.{token.value}'
                #         for decl in content:
                #             if decl.type == 'declaration' and decl.name == 'font-style':
                #                 if 'italic' in tinycss2.serialize(decl.value).strip():
                #                     print(class_name)
                #                     italic_classes.append(class_name)
                #                     break

    # return italic_classes


def epubExtractor(epub_path: str):
    chapter_files = _loadChapterFiles(epub_path)
    italic = _italicClasses(epub_path)
    print("Classes with italic formatting:")
    for cls in italic:
        print(cls)

# Replace with the path to your EPUB file
epubExtractor(r"C:\Users\jovanni\Desktop\Corey, James SA - The Expanse - 09 - Leviathan Falls.epub")

