import unittest
from scripts.c8_pilot_decision import nominate


class NominationTests(unittest.TestCase):
    def setup_table(self):
        plan={'formats':{'lower':'Q2_K','higher':'Q3_K'},'pairs':[{'first':'a','second':'b','eligible':True}]}
        table={}
        for rep in (1,2):
            for language in ('eng_Latn','ben_Beng','hin_Deva','pooled'):
                costs=(3.,1.,2.,1.) if language=='eng_Latn' else (2.,1.,3.,1.)
                for label,value in zip(('a::Q2_K','a::Q3_K','b::Q2_K','b::Q3_K'),costs):
                    table[rep,language,label]=value
        return plan,table

    def test_consistent_opposite_preferences_nominate(self):
        plan,costs=self.setup_table()
        result=nominate(plan,costs)
        self.assertIsNotNone(result['pair'])
        self.assertEqual(result['signs'],{'eng_Latn':1,'ben_Beng':-1})

    def test_instability_infeasibility_and_zero_margin_do_not_nominate(self):
        for change in ('unstable','infeasible','zero'):
            plan,costs=self.setup_table()
            if change=='unstable':
                costs[2,'ben_Beng','a::Q2_K']=4.
            elif change=='infeasible':
                plan['pairs'][0]['eligible']=False
            else:
                costs[1,'eng_Latn','a::Q2_K']=2.
            self.assertIsNone(nominate(plan,costs)['pair'])


if __name__=='__main__':
    unittest.main()
