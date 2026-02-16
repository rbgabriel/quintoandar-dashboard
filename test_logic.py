from quintoandar_scraper import slugify
import unittest

class TestScraper(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("São Paulo"), "sao-paulo")
        self.assertEqual(slugify("Rio de Janeiro"), "rio-de-janeiro")
        self.assertEqual(slugify("Copacabana"), "copacabana")

    def test_url_generation(self):
        # Mocking the logic found in main()
        def get_url(cidade, bairro=""):
            cidade_slug = slugify(cidade)
            if "sao-paulo" in cidade_slug:
                cidade_slug += "-sp"
            elif "rio-de-janeiro" in cidade_slug:
                cidade_slug += "-rj"
            
            if bairro:
                bairro_slug = slugify(bairro)
                return f"https://www.quintoandar.com.br/comprar/imovel/{bairro_slug}-{cidade_slug}-br"
            else:
                return f"https://www.quintoandar.com.br/comprar/imovel/{cidade_slug}"

        self.assertEqual(get_url("São Paulo"), "https://www.quintoandar.com.br/comprar/imovel/sao-paulo-sp")
        self.assertEqual(get_url("Rio de Janeiro"), "https://www.quintoandar.com.br/comprar/imovel/rio-de-janeiro-rj")
        self.assertEqual(get_url("Rio de Janeiro", "Copacabana"), "https://www.quintoandar.com.br/comprar/imovel/copacabana-rio-de-janeiro-rj-br")

if __name__ == "__main__":
    unittest.main()
