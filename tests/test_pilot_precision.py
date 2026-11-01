import unittest
from scripts.plan_pilot_precision import paired_scenario


class PlanningTests(unittest.TestCase):
    def test_accuracy_discordance_is_not_churn(self):
        correct=paired_scenario(300,23/300)
        churn=paired_scenario(300,33/300)
        self.assertLess(correct['standard_error'],churn['standard_error'])
        self.assertTrue(.45<correct['approximate_power_positive_or_negative_interval']<.50)
        self.assertLess(paired_scenario(424,23/300)['standard_error'],correct['standard_error'])

    def test_impossible_paired_scenarios_stop(self):
        for args in ((0,.1), (300,.01), (300,1.1)):
            with self.assertRaises(ValueError):
                paired_scenario(*args)


if __name__=='__main__':
    unittest.main()
