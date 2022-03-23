import unittest

from encoder.encoder import deserializer_file


class ProductVariableModelTest(unittest.TestCase):
    def test_content_banner(self):
        content = deserializer_file("resources/product_variable_model_1.txt")
        content.validate_variables()
        print(content)

    def test_content_banner_with_baston(self):
        content = deserializer_file("resources/product_variable_model_2.txt")
        content.validate_variables()
        print(content)

    def test_content_banner_with_profile(self):
        content = deserializer_file("resources/product_variable_model_3.txt")
        content.validate_variables()
        print(content)