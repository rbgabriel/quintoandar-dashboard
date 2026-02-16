import sys

def patch_scraper():
    path = "quintoandar_scraper.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Target snippet to replace
    old_target = """    if bairro:
        bairro_slug = slugify(bairro)
        if "sao-paulo" in cidade_slug:
            cidade_slug += "-sp"
        SEARCH_URL = f"https://www.quintoandar.com.br/comprar/imovel/{bairro_slug}-{cidade_slug}-br"
    else:
        if "sao-paulo" in cidade_slug:
            cidade_slug += "-sp"
        SEARCH_URL = f"https://www.quintoandar.com.br/comprar/imovel/{cidade_slug}"""

    # New snippet with RJ support
    new_snippet = """    if "sao-paulo" in cidade_slug:
        cidade_slug += "-sp"
    elif "rio-de-janeiro" in cidade_slug:
        cidade_slug += "-rj"

    if bairro:
        bairro_slug = slugify(bairro)
        SEARCH_URL = f"https://www.quintoandar.com.br/comprar/imovel/{bairro_slug}-{cidade_slug}-br"
    else:
        SEARCH_URL = f"https://www.quintoandar.com.br/comprar/imovel/{cidade_slug}"""

    if old_target in content:
        new_content = content.replace(old_target, new_snippet)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully patched quintoandar_scraper.py")
    else:
        # Try a slightly different target if indentation or whitespace differs
        print("Target not found. Checking for partial match...")
        if "sao-paulo" in content and "SEARCH_URL" in content:
            print("Found potential location, manual check needed or more flexible regex.")
        else:
            print("Target not found even partially.")

if __name__ == "__main__":
    patch_scraper()
