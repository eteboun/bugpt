from regulations.embedder import Embedder
from regulations.erasmus_regulations.regulation_parser import RegulationParser

class ErasmusRegulationEmbedder(Embedder):

    URL = "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662/"
    PARSER = RegulationParser
