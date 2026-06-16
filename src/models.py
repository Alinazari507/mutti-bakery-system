import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# ---------- User Roles ----------
class RoleType(Enum):
    ADMIN = "Mutti"
    MANAGER = "Manager"
    BAKER = "Baker"

class User:
    def __init__(self, username: str, role: RoleType):
        self.username = username
        self.role = role

    def can_approve_recipe(self) -> bool:
        return self.role == RoleType.ADMIN

    def can_scale(self) -> bool:
        return True

    def can_audit_log(self) -> bool:
        return self.role in [RoleType.ADMIN, RoleType.MANAGER]

# ---------- Ingredient & Conversion ----------
class Ingredient:
    def __init__(self, name: str, original_amount: float, original_unit: str):
        self.name = name
        self.original_amount = original_amount
        self.original_unit = original_unit
        self.normalized_grams: Optional[float] = None
        self.is_ambiguous = self._check_ambiguity()

    def _check_ambiguity(self) -> bool:
        ambiguous = ["pinch", "to taste", "as needed", "handful"]
        return self.original_unit.lower() in ambiguous

    def normalize(self, conversion_table: Dict[str, float]):
        if self.is_ambiguous:
            raise ValueError(f"Ambiguous unit '{self.original_unit}' for {self.name}")
        if self.original_unit not in conversion_table:
            raise ValueError(f"No conversion rule for {self.original_unit}")
        self.normalized_grams = self.original_amount * conversion_table[self.original_unit]
        return self.normalized_grams

    def to_dict(self):
        return {
            "name": self.name,
            "original_amount": self.original_amount,
            "original_unit": self.original_unit,
            "normalized_grams": self.normalized_grams,
            "is_ambiguous": self.is_ambiguous
        }

    @classmethod
    def from_dict(cls, data):
        ing = cls(data["name"], data["original_amount"], data["original_unit"])
        ing.normalized_grams = data.get("normalized_grams")
        ing.is_ambiguous = data.get("is_ambiguous", False)
        return ing

class NonLinearRule:
    def __init__(self, ingredient_name: str, max_multiplier: float, threshold_servings: int):
        self.ingredient_name = ingredient_name
        self.max_multiplier = max_multiplier
        self.threshold = threshold_servings

    def to_dict(self):
        return {"ingredient_name": self.ingredient_name, "max_multiplier": self.max_multiplier, "threshold": self.threshold}

    @classmethod
    def from_dict(cls, data):
        return cls(data["ingredient_name"], data["max_multiplier"], data["threshold"])

# ---------- Recipe Versioning ----------
class RecipeVersion:
    def __init__(self, version_id: int, recipe_id: str, ingredients: List[Ingredient],
                 non_linear_rules: List[NonLinearRule], base_servings: int,
                 mutti_approved: bool, modified_by: str, timestamp: str):
        self.version_id = version_id
        self.recipe_id = recipe_id
        self.ingredients = ingredients
        self.non_linear_rules = non_linear_rules
        self.base_servings = base_servings
        self.mutti_approved = mutti_approved
        self.modified_by = modified_by
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "version_id": self.version_id,
            "recipe_id": self.recipe_id,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "non_linear_rules": [r.to_dict() for r in self.non_linear_rules],
            "base_servings": self.base_servings,
            "mutti_approved": self.mutti_approved,
            "modified_by": self.modified_by,
            "timestamp": self.timestamp
        }

class Recipe:
    def __init__(self, recipe_id: str, name: str, category: str, base_servings: int):
        self.recipe_id = recipe_id
        self.name = name
        self.category = category
        self.base_servings = base_servings
        self.versions: List[RecipeVersion] = []

    def get_name(self): return self.name
    def get_category(self): return self.category
    def get_base_servings(self): return self.base_servings
    def get_versions(self): return self.versions

    def add_version(self, ingredients: List[Ingredient], rules: List[NonLinearRule],
                    mutti_approved: bool, modified_by: str) -> RecipeVersion:
        new_id = len(self.versions) + 1
        timestamp = datetime.now().isoformat()
        version = RecipeVersion(new_id, self.recipe_id, ingredients, rules,
                                self.base_servings, mutti_approved, modified_by, timestamp)
        self.versions.append(version)
        return version

    def get_current_version(self) -> Optional[RecipeVersion]:
        return self.versions[-1] if self.versions else None

    def scale(self, target_servings: int, role: str) -> Dict[str, Any]:
        version = self.get_current_version()
        if not version: raise ValueError("Recipe has no version")
        if not version.mutti_approved and role != "Mutti":
            raise PermissionError("Recipe not approved.")
        
        scaling_factor = target_servings / self.base_servings
        result = {}
        for ing in version.ingredients:
            rule = next((r for r in version.non_linear_rules if r.ingredient_name == ing.name), None)
            applied_factor = min(scaling_factor, rule.max_multiplier) if rule and target_servings > rule.threshold else scaling_factor
            scaled_grams = ing.normalized_grams * applied_factor
            result[ing.name] = {"rounded_g": self._round_quantity(scaled_grams), "note": "Linear" if not rule else "Non-linear"}
        return result

    def _round_quantity(self, grams: float) -> float:
        return round(grams / 5) * 5 if grams > 5 else round(grams)

    def expected_yield(self, target_servings: int) -> str:
        return f"Expected yield: ~{target_servings} portions."