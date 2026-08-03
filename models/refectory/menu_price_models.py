from dataclasses import dataclass, field, asdict

@dataclass
class PriceTableRow:
    category: str
    price: str
        
@dataclass
class PriceTable:
    label: str
    rows: list[PriceTableRow] = field(default_factory=list)

@dataclass
class MenuPrice:
    tables: list[PriceTable] = field(default_factory=list)

    def serialize(self) -> dict:
        return asdict(self)