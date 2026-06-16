# User Acceptance Test (UAT) Protocol – Mutti's Bakery System

**Project Name:** Mutti's Bakery Production System  
**Stakeholder:** Martha "Mutti" Klein  
**Test Date:** 16 June 2026  
**Test Environment:** Docker container (Ubuntu 24.04, Python 3.11)  
**Prepared By:** Mohammad Ali Nazari  

---

## 1. Test Summary

| Test Case ID | Description | Status (Pass/Fail) | Notes |
|--------------|-------------|--------------------|-------|
| TC-01 | Scale `mutti_bread_rolls` to 200 portions | ✅ Pass | |
| TC-02 | Scale to 500 portions – non‑linear salt cap (1.5×) | ✅ Pass | |
| TC-03 | Reject recipe with ambiguous unit (e.g., "pinch") | ✅ Pass | |
| TC-04 | Normalise 2 cups flour → 480g (using conversion table) | ✅ Pass | |
| TC-05 | Check rounding rules (<5g → 0.5g increments) | ✅ Pass | |

---

## 2. Detailed Test Execution

### TC-01: Scale to 200 portions
- **Precondition:** Recipe `mutti_bread_rolls` exists and is approved.  
- **Input:** `target = 200`  
- **Expected Result:** Flour → 9600g, Water → 6000g, Salt → 100g, Yeast → 300g, Sugar → 300g  
- **Actual Result:** Flour: 9600g, Water: 6000g, Salt: 100g, Yeast: 300g, Sugar: 300g  
- **Pass/Fail:** ✅ Pass

### TC-02: Non‑linear scaling at 500 portions
- **Precondition:** Recipe has non‑linear rule for Salt (max 1.5× above 500).  
- **Input:** `target = 500`  
- **Expected Result:** Salt quantity = 7.5g (not 25g linear)  
- **Actual Result:** Salt: 7.5g (Non-linear: capped at 1.5x)  
- **Pass/Fail:** ✅ Pass

### TC-03: Block ambiguous unit
- **Precondition:** Create a recipe with ingredient "pinch of salt".  
- **Input:** Try to add ingredient with unit "pinch".  
- **Expected Result:** System rejects ingredient and shows error about ambiguous unit.  
- **Actual Result:** `❌ Error setting ingredient: Ambiguous unit 'pinch' for salt. Ingredient not added.`  
- **Pass/Fail:** ✅ Pass

### TC-04: Unit normalisation
- **Precondition:** Conversion table has `cup = 240g`.  
- **Input:** Add ingredient "Flour: 2 cups".  
- **Expected Result:** Normalised grams = 480g.  
- **Actual Result:** flour: 480.0g (2 cups), sugar: 240.0g (1 cup)  
- **Pass/Fail:** ✅ Pass

### TC-05: Rounding rules
- **Precondition:** Base recipe with 10 portions.  
- **Input:** Scale to 55 portions.  
- **Expected Result:** Quantities rounded to nearest 0.5g, 5g, or 10g as per rules.  
- **Actual Result:** Flour: 2640g, Water: 1650g, Salt: 30g (rounded from 27.5), Yeast: 80g (rounded from 82.5), Sugar: 80g (rounded from 82.5)  
- **Pass/Fail:** ✅ Pass

---

## 3. Defect Log

| Defect ID | Description | Severity | Status |
|-----------|-------------|----------|--------|
| D-01 | Invalid Flake8 command syntax in GitHub Actions workflow. | Critical | Resolved |
| D-02 | Salt cap not effective due to rounding order (output 10.0g instead of 7.5g). | Medium | Resolved |
| D-03 | LaTeX formatting errors in UAT Protocol document. | Low | Resolved |

---

## 4. Final Decision

- [x] **Accepted** – System meets all business requirements.
- [ ] **Accepted with Minor Issues** – Issues listed in Defect Log, but system is usable.
- [ ] **Rejected** – Critical issues prevent production deployment.

---

## 5. Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Stakeholder (Mutti)** | Martha Klein | _________________ | ____/____/2026 |
| **Project Manager** | [Your PM's name] | _________________ | ____/____/2026 |
| **QA Lead** | Mohammad Ali Nazari | _________________ | ____/____/2026 |

---

*This document confirms that User Acceptance Testing has been completed and the system is ready for production deployment.*