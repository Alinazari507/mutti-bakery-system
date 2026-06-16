import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from ingredient import Ingredient


class NonLinearRule:
    """Limits structural multipliers for specific sensitive raw materials."""
    def __init__(self, ingredient_name: str, max_multiplier: float, threshold_servings: int):
        self.ingredient_name = ingredient_name
        self.max_multiplier = max_multiplier
        self.threshold = threshold_servings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ingredient_name": self.ingredient_name,
            "max_multiplier": self.max_multiplier,
            "threshold": self.threshold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NonLinearRule':
        return cls(
            ingredient_name=data["ingredient_name"],
            max_multiplier=data["max_multiplier"],
            threshold=data["threshold"]
        )


class RecipeVersion:
    """Historical tracking model to map version indices, audit logs, and approval metadata."""
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

    def to_dict(self) -> Dict[str, Any]:
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
    """Main recipe object controlling historical iterations and scaling parameters."""
    def __init__(self, recipe_id: str, name: str, category: str, base_servings: int):
        self._recipe_id = recipe_id
        self._name = name
        self._category = category
        self._base_servings = base_servings
        self._versions: List[RecipeVersion] = []
        self._current_version_id = 0

    def get_recipe_id(self) -> str:
        return self._recipe_id

    def get_name(self) -> str:
        return self._name

    def get_category(self) -> str:
        return self._category

    def get_base_servings(self) -> int:
        return self._base_servings

    def get_versions(self) -> List[RecipeVersion]:
        return list(self._versions)

    def get_current_version(self) -> Optional[RecipeVersion]:
        return self._versions[-1] if self._versions else None

    def add_version(self, ingredients: List[Ingredient], rules: List[NonLinearRule],
                    mutti_approved: bool, modified_by: str) -> RecipeVersion:
        new_id = len(self._versions) + 1
        timestamp = datetime.now().isoformat()
        version = RecipeVersion(
            version_id=new_id, recipe_id=self._recipe_id, ingredients=ingredients,
            non_linear_rules=rules, base_servings=self._base_servings,
            mutti_approved=mutti_approved, modified_by=modified_by, timestamp=timestamp
        )
        self._versions.append(version)
        self._current_version_id = new_id
        return version

    # ============================================================
    # FIXED: scale method with correct order of operations
    # (cap applied before rounding, then cap re-checked after rounding)
    # ============================================================
    def scale(self, target_servings: int, user_role: str) -> Dict[str, Any]:
        version = self.get_current_version()
        if not version:
            raise ValueError(f"Recipe '{self._name}' has no configured versions.")

        if not version.mutti_approved and user_role.upper() != "ADMIN":
            raise PermissionError("Scaling unapproved recipe version requires Admin role.")

        if not (10 <= target_servings <= 1000):
            raise ValueError("Target servings must be between 10 and 1000.")

        scaling_factor = target_servings / self._base_servings
        scaled_result = {}

        for ing in version.ingredients:
            grams = ing.get_normalized_grams()
            if grams is None:
                raise ValueError(f"Ingredient '{ing.get_name()}' not normalized.")

            rule = next((r for r in version.non_linear_rules if r.ingredient_name == ing.get_name()), None)

            # Step 1: raw linear scaling
            scaled_grams = grams * scaling_factor

            # Step 2: apply non-linear cap (before rounding)
            if rule and target_servings >= rule.threshold:
                max_allowed = grams * rule.max_multiplier
                scaled_grams = min(scaled_grams, max_allowed)
                note = f"Non-linear: capped at {rule.max_multiplier}x"
            else:
                note = "Linear scaling"

            # Step 3: rounding (FR-08)
            rounded_grams = self._round_quantity(scaled_grams)

            # Step 4: ensure rounded value does NOT exceed the cap
            if rule and target_servings >= rule.threshold:
                max_allowed = grams * rule.max_multiplier
                rounded_grams = min(rounded_grams, max_allowed)

            # cost calculation (unchanged)
            cost = (rounded_grams * (ing.get_cost_per_unit() / grams)) if grams > 0 else 0.0

            scaled_result[ing.get_name()] = {
                "original_g": round(grams, 2),
                "scaled_g": round(scaled_grams, 2),
                "rounded_g": rounded_grams,
                "cost": round(cost, 2),
                "unit": "g",
                "note": note
            }

        return scaled_result

    def calculate_cost(self, target_servings: int, user_role: str) -> float:
        try:
            data = self.scale(target_servings, user_role)
            return sum(item["cost"] for item in data.values())
        except Exception:
            return 0.0

    def _round_quantity(self, grams: float) -> float:
        if grams < 5:
            return round(grams * 2) / 2.0
        if grams <= 100:
            return round(grams / 5) * 5
        return round(grams / 10) * 10

    def expected_yield(self, target_servings: int, piece_weight_grams: float = 65) -> str:
        version = self.get_current_version()
        if not version:
            return "No versions available."
        total_grams = sum(i.get_normalized_grams() or 0.0 for i in version.ingredients)
        scaled_total_weight = total_grams * (target_servings / self._base_servings)
        pieces = scaled_total_weight / piece_weight_grams
        return f"Expected yield: ~{int(pieces)} pieces at approx. {piece_weight_grams}g each"

    def get_info_scaled(self, target_servings: int, user_role: str) -> str:
        scaled = self.scale(target_servings, user_role)
        total_cost = self.calculate_cost(target_servings, user_role)
        lines = []
        for name, data in scaled.items():
            lines.append(f"{name:<20} {data['rounded_g']:>8.1f} {data['cost']:>10.2f}€  {data['note']}")
        lines.append("-" * 72)
        lines.append(f"{'Total Recipe Cost:':<30} {total_cost:>10.2f}€")
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"[{self._category}] {self._name} (Base servings: {self._base_servings})"