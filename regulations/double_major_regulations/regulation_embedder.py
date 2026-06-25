from regulations.embedder import Embedder
from regulations.double_major_regulations.regulation_parser import RegulationParser

class DoubleMajorRegulationEmbedder(Embedder):

    URL = "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661"
    PARSER = RegulationParser
