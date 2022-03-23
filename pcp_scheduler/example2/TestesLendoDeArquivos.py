import unittest
from encoder.encoder import deserializer_file
from pcp_scheduler.src.scheduler.scheduler import Allocator
from pcp_scheduler.src.scheduler.scheduler_ag import generate_allocation


class SerializedTestCase(unittest.TestCase):
    def test_allocator_from_file(self):
        content = deserializer_file("input.txt")
        allocator = Allocator(content['grid'], content['planjobs'], content['configs'])
        allocator.generate_allocation()

    def test_scheduler_from_file(self):
        content = deserializer_file("input.txt")
        result = generate_allocation(content['grid'], content['planjobs'], content['configs'])
        print(result)

if __name__ == '__main__':
    unittest.main()
