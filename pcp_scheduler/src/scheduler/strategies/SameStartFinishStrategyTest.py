import unittest

from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.scheduler.strategies.SameStartFinishStrategy import build_schema
from pcp_scheduler.utils import test_utils


class SameStartFinishStrategyTestCase(unittest.TestCase):

    def test_build_schema(self):
        planjob_a = Planjob(120, 'a')
        planjob_b = Planjob(80, 'b')
        planjob_c = Planjob(30, 'c')
        planjob_d = Planjob(40, 'd')
        planjob_e = Planjob(90, 'e')

        planjob_a.same_start = ['b']
        planjob_a.same_finish = ['d', 'e']
        planjob_b.same_start = ['a']
        planjob_b.same_finish = ['c']
        planjob_c.same_start = ['d', 'e']
        planjob_c.same_finish = ['b']
        planjob_d.same_start = ['c', 'e']
        planjob_d.same_finish = ['a', 'e']
        planjob_e.same_start = ['c', 'd']
        planjob_e.same_finish = ['a', 'd']

        requirements = build_schema([planjob_a, planjob_b, planjob_c, planjob_d, planjob_e])
        self.assertEquals(len(requirements), 5)

        planjob_a = Planjob(120, 'a')
        planjob_b = Planjob(120, 'b')
        planjob_a.same_start = ['b']
        planjob_b.same_start = ['a']
        requirements = build_schema([planjob_a, planjob_b])

        self.assertEquals(len(requirements), 2)
        self.assertEquals(len(requirements[0].slots), 1)
        self.assertEquals(len(requirements[1].slots), 1)
        self.assertEquals(requirements[0].slots, requirements[1].slots)

        planjob_a = Planjob(80, 'a')
        planjob_b = Planjob(120, 'b')
        planjob_a.same_start = ['b']
        planjob_a.same_finish = ['b']
        planjob_b.same_start = ['a']
        planjob_b.same_finish = ['a']

        requirements = build_schema([planjob_a, planjob_b])

        self.assertEquals(len(requirements), 2)
        self.assertTrue(len(requirements[0].slots) == 2 or len(requirements[1].slots) == 2)
        self.assertEquals(requirements[0].start(), requirements[1].start())
        self.assertEquals(requirements[0].finish(), requirements[1].finish())

        planjob_a = Planjob(40, 'a')
        planjob_b = Planjob(120, 'b')
        planjob_c = Planjob(40, 'c')
        planjob_a.same_start = ['b']
        planjob_b.same_start = ['a']
        planjob_b.same_finish = ['c']
        planjob_c.same_finish = ['b']

        planjobs = [planjob_a, planjob_b, planjob_c]
        requirements = build_schema(planjobs)

        self.assertEquals(len(requirements), 3)
        self.assertEquals(len(requirements[0].slots), 1)
        self.assertEquals(len(requirements[1].slots), 1)
        self.assertEquals(len(requirements[2].slots), 1)

        req_a = test_utils.get_requirement_by_id(requirements, planjob_a.id)
        req_b = test_utils.get_requirement_by_id(requirements, planjob_b.id)
        req_c = test_utils.get_requirement_by_id(requirements, planjob_c.id)

        self.assertEquals(req_a.start(), req_b.start())
        self.assertEquals(req_b.finish(), req_c.finish())

        planjob_a = Planjob(40, 'a')
        planjob_b = Planjob(40, 'b')
        planjob_c = Planjob(40, 'c')
        planjob_d = Planjob(40, 'd')

        planjob_a.same_start = ['b']
        planjob_b.same_start = ['a']
        planjob_b.same_finish = ['c']
        planjob_c.same_finish = ['b']
        planjob_c.same_start = ['d']
        planjob_d.same_start = ['c']

        planjobs = [planjob_a, planjob_b, planjob_c, planjob_d]
        requirements = build_schema(planjobs)

        self.assertEquals(len(requirements), 4)
        self.assertEquals(len(requirements[0].slots), 1)
        self.assertEquals(len(requirements[1].slots), 1)
        self.assertEquals(len(requirements[2].slots), 1)
        self.assertEquals(len(requirements[3].slots), 1)

        req_a = test_utils.get_requirement_by_id(requirements, planjob_a.id)
        req_b = test_utils.get_requirement_by_id(requirements, planjob_b.id)
        req_c = test_utils.get_requirement_by_id(requirements, planjob_c.id)
        req_d = test_utils.get_requirement_by_id(requirements, planjob_d.id)

        self.assertEquals(req_a.start(), req_b.start())
        self.assertEquals(req_b.finish(), req_c.finish())
        self.assertEquals(req_c.start(), req_d.start())


if __name__ == '__main__':
    unittest.main()
