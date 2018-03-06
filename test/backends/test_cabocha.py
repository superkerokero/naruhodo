import unittest
from naruhodo.backends.cabocha import CabochaClient

class TestCabochaClient(unittest.TestCase):
    """
    Unit test for cabocha backend.
    """

    def test_add(self):
        cabo = CabochaClient()
        text = '* 0 2D 1/2 0.698846\n麻生\t名詞,固有名詞,人名,姓,*,*,麻生,アソウ,アソー\n太郎\t名詞,固有名詞,人名,名,*,*,太郎,タロウ,タロー\nは\t助詞,係助詞,*,*,*,*,は,ハ,ワ\n* 1 2D 0/1 3.258964\nコーヒー\t名詞,一般,*,*,*,*,コーヒー,コーヒー,コーヒー\nを\t助詞,格助詞,一般,*,*,*,を,ヲ,ヲ\n* 2 -1D 0/2 1.034467\n飲み\t動詞,自立,*,*,五段・マ行,連用形,飲む,ノミ,ノミ\nませ\t助動詞,*,*,*,特殊・マス,未然形,ます,マセ,マセ\nん\t助動詞,*,*,*,不変化型,基本形,ん,ン,ン\n。\t記号,句点,*,*,*,*,。,。,。\n'
        cabo.add(text)
        self.assertEqual(cabo.chunks[0].main, "麻生\n太郎")
        self.assertEqual(cabo.chunks[1].main, "コーヒー")
        self.assertEqual(cabo.chunks[2].main, "飲む(否定)")
        self.assertEqual(cabo.chunks[0].func, "は")
        self.assertEqual(cabo.chunks[1].func, "を")
        self.assertEqual(cabo.chunks[2].func, "ませ・ん")
        self.assertEqual(cabo.chunks[0].type, 0)
        self.assertEqual(cabo.chunks[1].type, 0)
        self.assertEqual(cabo.chunks[2].type, 2)
        self.assertEqual(cabo.chunks[0].NE, 1)
        text = '* 0 4D 0/0 0.374646\nそして\t接続詞,*,*,*,*,*,そして,ソシテ,ソシテ\n* 1 4D 0/1 1.891652\n彼\t名詞,代名詞,一般,*,*,*,彼,カレ,カレ\nは\t助詞,係助詞,*,*,*,*,は,ハ,ワ\n* 2 3D 0/1 1.693876\n東京\t名詞,固有名詞,地域,一般,*,*,東京,トウキョウ,トーキョー\nの\t助詞,連体化,*,*,*,*,の,ノ,ノ\n* 3 4D 0/1 3.798380\n家\t名詞,一般,*,*,*,*,家,イエ,イエ\nに\t助詞,格助詞,一般,*,*,*,に,ニ,ニ\n* 4 -1D 0/1 1.307374\n帰っ\t動詞,自立,*,*,五段・ラ行,連用タ接続,帰る,カエッ,カエッ\nた\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ\n。\t記号,句点,*,*,*,*,。,。,。\n'
        cabo.add(text)
        self.assertEqual(cabo.chunks[3].main, "そして")
        self.assertEqual(cabo.chunks[4].main, "彼[0@0]")
        self.assertEqual(cabo.chunks[5].main, "東京")
        self.assertEqual(cabo.chunks[3].func, "")
        self.assertEqual(cabo.chunks[4].func, "は")
        self.assertEqual(cabo.chunks[5].func, "の")
        self.assertEqual(cabo.chunks[3].type, 3)
        self.assertEqual(cabo.chunks[4].type, 0)
        self.assertEqual(cabo.chunks[5].type, 0)
        self.assertEqual(cabo.chunks[4].pro, 4)
