import os
import yaml
import json
from jinja2 import Environment, FileSystemLoader

# Load the site.yaml file
with open("config.yaml", "r") as file:
    site_data = yaml.safe_load(file)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"), autoescape=False)

# Create output directory if it doesn't exist
if not os.path.exists("output"):
    os.makedirs("output")

# Process each page and render the templates
for page in site_data["pages"]:
    # Load the page template
    template = env.get_template(page["template"])

    has_multiple_sections = False
    if "sections" in page.keys():
        has_multiple_sections = len(page["sections"]) > 1

    if has_multiple_sections:
        rendered_sections = []
        
        for section in page["sections"]:
            print(f"Rendering section {section['title']}")
            for idx, meta in enumerate(section["metadata"]):
                try:
                    if "content_file" in meta.keys():
                        with open(meta["content_file"]) as content_file:
                            section["metadata"][idx]["content_file"] = content_file.read()
                    elif "data_dict" in meta.keys():
                        with open(meta["data_dict"]) as data_file:
                            section["metadata"][idx]["data_dict"] = json.load(data_file)
                except Exception as e:
                    print(f"Error processing {meta['content_file']}: {e}")
            section_template = env.get_template(section["section_template"])
            temp_metadata = {k: v for d in section["metadata"] for k, v in d.items()}
            section["metadata"] = temp_metadata
            rendered_sections.append(section_template.render(section=section, site=site_data))
        rendered_page = template.render(page=page, sections=rendered_sections, site=site_data)
    else:
        rendered_page = template.render(page=page)

    page_link = page["permalink"].lstrip("/") + ".html"
    if page_link == ".html":
        page_link = "index.html"
    

    # Save the rendered page
    with open(os.path.join("docs", page_link), "w") as output_file:
        output_file.write(rendered_page)

print("Static site generated successfully!")
