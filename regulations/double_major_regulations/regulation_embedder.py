from regulations.embedder import Embedder
from regulation_parser import RegulationParser

class RegulationEmbedder(Embedder):

    URL = "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661"
    PARSER = RegulationParser

print(RegulationEmbedder._get_chunks())