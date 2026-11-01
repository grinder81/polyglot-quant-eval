import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
from scripts.prepare_ted_pilot_pool import aligned_rows
from scripts.prepare_compression_pilot_pool import normalized_source


class PoolIdentityTests(unittest.TestCase):
    def test_source_scheme_escaping_and_underscore(self):
        self.assertEqual(normalized_source('http://en.wikinews.org/wiki/A_B%27s/'),
                         normalized_source('https://en.wikinews.org/wiki/A B\'s'))

    def test_moses_document_boundary_and_sentence_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bn-en.zip'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('TED2020.bn-en.bn','bn1\n\nbn2\n\n')
                archive.writestr('TED2020.bn-en.en','en1\n\nen2\n\n')
                archive.writestr('TED2020.bn-en.xml','<cesAlign><linkGrp fromDoc="bn/ted2020-1.xml.gz" toDoc="en/ted2020-1.xml.gz"><link xtargets="3;5"/></linkGrp><linkGrp fromDoc="bn/ted2020-2.xml.gz" toDoc="en/ted2020-2.xml.gz"><link xtargets="7;9"/></linkGrp></cesAlign>')
            self.assertEqual(aligned_rows(path,'bn-en'),{('1','5'):{'en':'en1','other':'bn1'},('2','9'):{'en':'en2','other':'bn2'}})
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('TED2020.bn-en.bn','bn1\n')
                archive.writestr('TED2020.bn-en.en','en1\n')
                archive.writestr('TED2020.bn-en.xml','<cesAlign><linkGrp fromDoc="bn/ted2020-1.xml.gz" toDoc="en/ted2020-2.xml.gz"><link xtargets="3;5"/></linkGrp></cesAlign>')
            with self.assertRaises(ValueError):
                aligned_rows(path,'bn-en')


if __name__=='__main__':
    unittest.main()
