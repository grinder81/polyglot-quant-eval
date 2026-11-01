import unittest
from scripts.summarize_t3_curve import require_final_stages


class StageGates(unittest.TestCase):
    def outcome(self,english):
        return {'vs_bf16':{'languages':{'eng_Latn':{'candidate_correct':english}}}}

    def test_cannot_select_point_from_an_incomplete_unstopped_curve(self):
        with self.assertRaises(ValueError):
            require_final_stages({'diag-q6k':self.outcome(230),'diag-q3km':self.outcome(220)})

    def test_early_stop_and_actual_size_nonmonotonicity(self):
        require_final_stages({'diag-q6k':self.outcome(230),'diag-q3km':self.outcome(185)})
        partial={name:self.outcome(220) for name in ('diag-q6k','diag-q3km','diag-q3ks','diag-q2k')}
        partial['diag-q2k']=self.outcome(160)
        with self.assertRaises(ValueError):
            require_final_stages(partial)
        partial['diag-iq3s']=self.outcome(221)
        require_final_stages(partial)


if __name__=='__main__':
    unittest.main()
