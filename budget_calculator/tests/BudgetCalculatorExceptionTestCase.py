import unittest
from encoder.encoder import deserializer_file
from budget_calculator.main import budget_calc


class BudgetCalculatorExceptionTestCase(unittest.TestCase):
    def test_invalid_unit_measurement_cast(self):
        self.assertEqual("","");

    def test_simulator(self):
        content = deserializer_file("flexibleprinting.txt")
        budget_calculator = budget_calc(content.data)

    def test_refile(self):
        content = deserializer_file("refilemanual.txt")
        budget_calculator = budget_calc(content.data)

    def test_content_transparent_vinyl(self):
        content = deserializer_file("inputtransparentvinyl.txt")
        budget_calculator = budget_calc(content.data)

    def test_new_test(self):
        content = deserializer_file("new_test.txt")
        budget_calculator = budget_calc(content.data)
        print(budget_calculator)

    def test_banner(self):
        content = deserializer_file("banner.txt")
        budget_calculator = budget_calc(content.data)

    def test_banner_with_baston(self):
        content = deserializer_file("banner_with_baston.txt")
        budget_calculator = budget_calc(content.data)

    def test_banner_with_profile(self):
        content = deserializer_file("banner_with_profile.txt")
        budget_calculator = budget_calc(content.data)
        print(budget_calculator)


if __name__ == '__main__':
    unittest.main()
