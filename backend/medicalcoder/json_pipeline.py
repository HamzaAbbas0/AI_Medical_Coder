import requests
from bs4 import BeautifulSoup
import json
import re
from collections import defaultdict
import os


# ---------------------------------------------------------------------
# 1️⃣ Build ICD-10 URL dynamically based on code like F11 or G47
# ---------------------------------------------------------------------
def construct_icd10_url(code):
    """Construct ICD-10 URL dynamically (e.g., F11 → .../F11-/)"""
    code = code.upper().strip()

    if not re.match(r'^[A-Z]\d{2}$', code):
        raise ValueError(f"Invalid ICD-10 code format: {code}. Should be like F11, G47, etc.")

    letter = code[0]
    first_digit = code[1]
    second_digit = code[2]

    full_range = f"{letter}00-{letter}99"
    sub_range = f"{letter}{first_digit}{second_digit}-{letter}{first_digit}{second_digit}"
    base_url = "https://www.icd10data.com/ICD10CM/Codes"
    return f"{base_url}/{full_range}/{sub_range}/{code}-"


# ---------------------------------------------------------------------
# 2️⃣ Parse the HTML hierarchy recursively
# ---------------------------------------------------------------------
def parse_tree(ul, parent_code=None, parent_desc=None, data_list=None):
    """Recursively parse ICD hierarchy and record parent–child pairs."""
    for li in ul.find_all("li", recursive=False):
        span = li.find("span", id=True)
        if not span:
            continue

        code = span.get("id").strip()
        desc = span.get_text(" ", strip=True)
        if desc.startswith(code):
            desc = desc[len(code):].strip(" :-")

        data_list.append({
            "Parent Code": parent_code or code,
            "Parent Description": parent_desc or desc if not parent_code else parent_desc,
            "Child Code": code if parent_code else "",
            "Child Description": desc if parent_code else ""
        })

        child_ul = li.find("ul", class_="tree", recursive=False)
        if child_ul:
            parse_tree(child_ul, parent_code=code, parent_desc=desc, data_list=data_list)


# ---------------------------------------------------------------------
# 3️⃣ Scrape ICD codes from the constructed URL
# ---------------------------------------------------------------------
def scrape_icd_codes(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch page (status {response.status_code})")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ Get correct UL after the “Codes” header
    code_ul = None
    code_header = soup.find("h2", string=re.compile(r"^Codes", re.I))
    if code_header:
        code_ul = code_header.find_next_sibling("ul", class_="codeHierarchy")

    # Fallback if not found (some pages have slightly different layouts)
    if not code_ul:
        all_hierarchies = soup.find_all("ul", class_="codeHierarchy")
        if all_hierarchies:
            code_ul = all_hierarchies[-1]  # last one usually contains the actual codes

    if not code_ul:
        print("❌ No hierarchy found — maybe invalid code or structure changed.")
        return []

    data = []
    parse_tree(code_ul, data_list=data)
    return data


# ---------------------------------------------------------------------
# 4️⃣ Convert flat pairs into nested hierarchical JSON
# ---------------------------------------------------------------------
def build_hierarchy(flat_data):
    """Build nested JSON hierarchy."""
    children_map = defaultdict(list)
    desc_map = {}

    for item in flat_data:
        parent = item["Parent Code"]
        child = item["Child Code"]
        parent_desc = item["Parent Description"]
        child_desc = item["Child Description"]

        if parent not in desc_map or not desc_map[parent]:
            desc_map[parent] = parent_desc or child_desc

        if child:
            children_map[parent].append({
                "code": child,
                "description": child_desc,
                "children": []
            })

    def nest_children(code, desc=None):
        node = {
            "code": code,
            "description": desc or desc_map.get(code, ""),
            "children": []
        }
        for child in children_map.get(code, []):
            node["children"].append(nest_children(child["code"], child["description"]))
        return node

    all_codes = set(desc_map.keys())
    child_codes = {item["Child Code"] for item in flat_data if item["Child Code"]}
    top_level = list(all_codes - child_codes)

    return [nest_children(code, desc_map.get(code)) for code in top_level]


# ---------------------------------------------------------------------
# 5️⃣ Save hierarchy as readable text file
# ---------------------------------------------------------------------
def save_icd_to_text(nested_data, code):
    """Save ICD hierarchy as indented text file."""
    output_file = f"icd_hierarchy_{code}_codes.txt"

    def write_node(node, level=0, lines=None):
        if lines is None:
            lines = []
        indent = "    " * level
        line = f"{indent}{node['code']}: {node['description']}"
        lines.append(line)
        for child in node.get("children", []):
            write_node(child, level + 1, lines)
        return lines

    all_lines = []
    for entry in nested_data:
        all_lines.extend(write_node(entry))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))

    print(f"[✔] Saved hierarchy text file: {output_file}")


# ---------------------------------------------------------------------
# 6️⃣ Master function — runs full pipeline
# ---------------------------------------------------------------------
def get_icd_hierarchy(code):
    """
    Full ICD-10 pipeline:
      1. Build URL
      2. Scrape hierarchy (Codes only)
      3. Build nested JSON
      4. Save readable text
    """
    url = construct_icd10_url(code)
    print(f"\n🔍 Fetching data from: {url}\n")

    flat_data = scrape_icd_codes(url)
    if not flat_data:
        print("No data found.")
        return [], ""

    nested_data = build_hierarchy(flat_data)

    # Save text file
    save_icd_to_text(nested_data, code)

    # Build printable text
    lines = []

    def write_node(node, level=0):
        indent = "    " * level
        lines.append(f"{indent}{node['code']}: {node['description']}")
        for child in node.get("children", []):
            write_node(child, level + 1)

    for entry in nested_data:
        write_node(entry)

    text_output = "\n".join(lines)
    print(f"[✔] Hierarchy for {code} extracted successfully!")
    return nested_data, text_output


# ---------------------------------------------------------------------
# 7️⃣ Run interactively
# ---------------------------------------------------------------------
if __name__ == "__main__":
    code_input = input("Enter ICD-10 Code (e.g., F11, G47): ").strip().upper()
    try:
        data, text = get_icd_hierarchy(code_input)
        print("\n✅ Extraction Complete.\n")
        print(text)
    except Exception as e:
        print(f"❌ Error: {e}")