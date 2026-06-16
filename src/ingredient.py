import json
from typing import Dict, Any

class Ingredient:
    """
    Represents a single ingredient with units, cost, normalization,
    and ambiguity checks. Fully encapsulated using private variables.
    """
    def __init__(self, name: str, original_amount: float, original_unit: str, cost_per_unit: float):
        self._name = name
        self._original_amount = original_amount
        self._original_unit = original_unit
        self._cost_per_unit = cost_per_unit
        self._normalized_grams = None
        self._is_ambiguous = self._check_ambiguity()

    # Getters
    def get_name(self) -> str:
        return self._name

    def get_original_amount(self) -> float:
        return self._original_amount

    def get_original_unit(self) -> str:
        return self._original_unit

    def get_cost_per_unit(self) -> float:
        return self._cost_per_unit

    def get_normalized_grams(self) -> float:
        return self._normalized_grams

    def is_ambiguous(self) -> bool:
        return self._is_ambiguous

    # Setters
    def set_cost_per_unit(self, value: float) -> None:
        if value < 0:
            raise ValueError("Cost cannot be negative.")
        self._cost_per_unit = value

    def set_normalized_grams(self, value: float) -> None:
        if value is not None and value < 0:
            raise ValueError("Normalized grams cannot be negative.")
        self._normalized_grams = value

    # Helper validation functions
    def _check_ambiguity(self) -> bool:
        ambiguous_units = ["pinch", "to taste", "as needed", "handful"]
        return self._original_unit.lower().strip() in ambiguous_units

    def normalize(self, conversion_table: Dict[str, float]) -> float:
        if self._is_ambiguous:
            raise ValueError(f"Ambiguous unit '{self._original_unit}' for {self._name}")
        
        unit_key = self._original_unit.lower().strip()
        if unit_key not in conversion_table:
            raise ValueError(f"No conversion rule for unit: '{self._original_unit}'")
        
        self._normalized_grams = self._original_amount * conversion_table[unit_key]
        return self._normalized_grams

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "original_amount": self._original_amount,
            "original_unit": self._original_unit,
            "cost_per_unit": self._cost_per_unit,
            "normalized_grams": self._normalized_grams,
            "is_ambiguous": self._is_ambiguous
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ingredient':
        ing = cls(
            name=data["name"],
            original_amount=data["original_amount"],
            original_unit=data["original_unit"],
            cost_per_unit=data.get("cost_per_unit", 0.0)
        )
        ing._normalized_grams = data.get("normalized_grams")
        ing._is_ambiguous = data.get("is_ambiguous", False)
        return ing

    def __str__(self) -> str:
        cost_str = f" @ {self._cost_per_unit:.4f} €/{self._original_unit}" if self._cost_per_unit > 0 else ""
        return f"{self._name}: {self._original_amount} {self._original_unit}{cost_str}"