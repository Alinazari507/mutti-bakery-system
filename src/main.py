#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Ensure we can import modules from the current directory
sys.path.insert(0, os.path.dirname(__file__))

from auth import User, RoleType
from ingredient import Ingredient
from recipe import Recipe, NonLinearRule, RecipeVersion
from cache import ScalingCache
from break_glass import emergency_break_glass

# Set base directory to the project root (one level up from src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
RECIPES_FILE = os.path.join(BASE_DIR, "data", "recipes.json")
CONVERSIONS_FILE = os.path.join(BASE_DIR, "data", "conversions.json")

class AuditLog:
    @classmethod
    def log(cls, action: str, user: str, details: str):
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] USER={user} ACTION={action} DETAILS={details}\n"
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f" Logged: {action} by {user}")

def load_conversion_table() -> Dict[str, float]:
    try:
        with open(CONVERSIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "cup": 240.0,
            "tablespoon": 15.0,
            "teaspoon": 5.0,
            "g": 1.0,
            "kg": 1000.0,
            "ml": 1.0,
            "l": 1000.0,
            "each": 50.0
        }

def load_recipes() -> Dict:
    try:
        with open(RECIPES_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}

    recipes = {}
    for rid, rdata in data.items():
        recipe = Recipe(rid, rdata["name"], rdata.get("category", "General"), rdata["base_servings"])
        for vdata in rdata.get("versions", []):
            ingredients = [Ingredient.from_dict(i) for i in vdata["ingredients"]]
            rules = []
            version = RecipeVersion(
                vdata["version_id"], rid, ingredients, rules,
                vdata["base_servings"], vdata["mutti_approved"],
                vdata["modified_by"], vdata["timestamp"]
            )
            recipe._versions.append(version)
        recipe._current_version_id = len(recipe._versions)
        recipes[rid] = recipe
    return recipes

def save_recipes(recipes: Dict):
    data = {}
    for rid, recipe in recipes.items():
        data[rid] = {
            "name": recipe.get_name(),
            "category": recipe.get_category(),
            "base_servings": recipe.get_base_servings(),
            "versions": [v.to_dict() for v in recipe.get_versions()]
        }
    os.makedirs(os.path.dirname(RECIPES_FILE), exist_ok=True)
    with open(RECIPES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def login() -> User:
    print("=" * 55)
    print("          MUTTI'S BAKERY PRODUCTION SYSTEM        ")
    print("=" * 55)
    username = input("Username: ").strip()
    role_input = input("Role (admin/manager/baker): ").lower().strip()
    if role_input == "admin":
        role = RoleType.ADMIN
    elif role_input == "manager":
        role = RoleType.MANAGER
    else:
        role = RoleType.BAKER
    return User(username, role)

def main():
    recipes = load_recipes()
    conversion_table = load_conversion_table()
    cache = ScalingCache()
    
    current_user = login()
    AuditLog.log("LOGIN", current_user.username, f"Role={current_user.role.value}")

    # BAKER Mode (Read-Only)
    if current_user.role == RoleType.BAKER:
        print("\n--- BAKER SHIFT MODE (Read-only Recipe Scaling) ---")
        if not recipes:
            print("No recipes loaded. Please ask a Manager or Mutti to configure data.")
            return
        for rid, rec in recipes.items():
            print(f"- {rec.get_name()} ({rec.get_category()})")
        
        rid = input("\nEnter recipe ID to scale: ").strip()
        if rid not in recipes:
            print("❌ Invalid recipe ID.")
            return
        recipe = recipes[rid]
        try:
            target = int(input("Portions (10-1000): "))
            cached = cache.get(rid, target)
            if cached:
                print("\n")
                scaled = cached
            else:
                scaled = recipe.scale(target, current_user.role.value)
                cache.set(rid, target, scaled)

            print("\nScaled Recipe Sheet:")
            for ing_name, data in scaled.items():
                print(f" {ing_name}: {data['rounded_g']}g ({data['note']})")
            print(recipe.expected_yield(target))
            AuditLog.log("SCALE_BAKER", current_user.username, f"Scaled {rid} to {target}")
        except Exception as e:
            print(f"❌ Error: {e}")
            AuditLog.log("ERROR", current_user.username, str(e))
        return

    # Admin / Manager Menu
    while True:
        print("\n" + "-" * 30 + " MAIN MENU " + "-" * 30)
        print("1. List Available Recipes")
        print("2. Construct and Save New Recipe (Draft Version)")
        print("3. Scale and Calculate Production Costs")
        print("4. Mutti Recipe Approval (Admin Only)")
        print("5. Emergency Break-Glass (Elevate Privileges)")
        print("6. Exit Production System")
        choice = input("Enter option (1-6): ").strip()

        if choice == "1":
            print("\n--- Current System Recipe Registry ---")
            for rid, rec in recipes.items():
                ver = rec.get_current_version()
                approved = ver.mutti_approved if ver else False
                print(f"- ID: {rid:<20} | Name: {rec.get_name():<25} | Approved: {str(approved):<6} | Category: {rec.get_category()}")

        elif choice == "2":
            name = input("Recipe Name: ").strip()
            category = input("Category (Bread/Cake/Pastry): ").strip()
            try:
                base = int(input("Base Servings (e.g. 10): "))
            except ValueError:
                print("❌ Invalid serving number.")
                continue
            
            rid = name.lower().replace(" ", "_")
            if rid in recipes:
                print("❌ Recipe already exists. Delete or select a different name.")
                continue

            recipe = Recipe(rid, name, category, base)
            ingredients = []
            print("\n--- Adding Ingredients ---")
            while True:
                ing_name = input("Ingredient name (leave blank to stop): ").strip()
                if not ing_name:
                    break
                try:
                    amount = float(input(f"Amount for {ing_name}: "))
                    unit = input(f"Unit (cup, ml, g, tbsp, tsp, each): ").strip()
                    cost = float(input(f"Cost per unit (€): "))
                    
                    ing = Ingredient(ing_name, amount, unit, cost)
                    ing.normalize(conversion_table)
                    ingredients.append(ing)
                except Exception as e:
                    print(f"❌ Error setting ingredient: {e}. Ingredient not added.")

            rules = []
            add_rule = input("\nAdd custom scaling non-linear rule? (y/n): ").lower().strip()
            if add_rule == 'y':
                ing_name = input("Target ingredient name: ").strip()
                try:
                    max_mult = float(input("Maximum safety multiplier (e.g. 1.5): "))
                    threshold = int(input("Active threshold serving size limit: "))
                    rules.append(NonLinearRule(ing_name, max_mult, threshold))
                except ValueError:
                    print("❌ Invalid rule constraints entered. Skipping rule creation.")

            approved = False
            if current_user.can_approve_recipe():
                ans = input("\nApprove this recipe version immediately? (y/n): ").lower().strip()
                approved = (ans == 'y')

            recipe.add_version(ingredients, rules, approved, current_user.username)
            recipes[rid] = recipe
            save_recipes(recipes)
            AuditLog.log("CREATE_RECIPE", current_user.username, f"Created {rid} (Approved={approved})")
            print("✔ Recipe saved successfully.")

        elif choice == "3":
            rid = input("Recipe ID to scale: ").strip()
            if rid not in recipes:
                print("❌ Recipe not found.")
                continue
            recipe = recipes[rid]
            try:
                target = int(input("Target Portion Size (10-1000): "))
                cached = cache.get(rid, target)
                if cached:
                    print("\n")
                    scaled = cached
                else:
                    scaled = recipe.scale(target, current_user.role.value)
                    cache.set(rid, target, scaled)
                
                print("\n" + "=" * 50)
                print(recipe.get_info_scaled(target, current_user.role.value))
                print(recipe.expected_yield(target))
                print("=" * 50)
                AuditLog.log("SCALE", current_user.username, f"Scaled {rid} to {target} portions")
            except Exception as e:
                print(f"❌ Error during scaling: {e}")
                AuditLog.log("ERROR", current_user.username, str(e))

        elif choice == "4":
            if not current_user.can_approve_recipe():
                print("❌ Access denied. Only Mutti (Admin) has recipe approval privileges.")
                AuditLog.log("UNAUTHORIZED_APPROVE_ATTEMPT", current_user.username, "")
                continue

            rid = input("Recipe ID to sign-off and approve: ").strip()
            if rid not in recipes:
                print("❌ Recipe not found.")
                continue
            recipe = recipes[rid]
            curr = recipe.get_current_version()
            if not curr:
                print("❌ No versions of this recipe exist to approve.")
                continue

            recipe.add_version(curr.ingredients, curr.non_linear_rules, True, current_user.username)
            save_recipes(recipes)
            AuditLog.log("APPROVE_RECIPE", current_user.username, rid)
            print(f"✔ Recipe '{recipe.get_name()}' successfully approved and active.")

        elif choice == "5":
            if current_user.role == RoleType.ADMIN:
                print("You are already authenticated with Administrator privileges.")
                continue
            
            temp_admin = emergency_break_glass(AuditLog.log)
            if temp_admin:
                current_user = temp_admin
                print(f"✔ Active privileges upgraded to: {current_user.role.value}")

        elif choice == "6":
            print("Exiting Mutti's Bakery system. Goodbye!")
            break

if __name__ == "__main__":
    main()