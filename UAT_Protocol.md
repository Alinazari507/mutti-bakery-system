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
| TC-01 | Scale `mutti_bread_rolls` to 200 portions | ⬜ | |
| TC-02 | Scale to 500 portions – non‑linear salt cap (1.5×) | ⬜ | |
| TC-03 | Reject recipe with ambiguous unit (e.g., "pinch") | ⬜ | |
| TC-04 | Normalise 2 cups flour → 480g (using conversion table) | ⬜ | |
| TC-05 | Check rounding rules (<5g → 0.5g increments) | ⬜ | |

---

## 2. Detailed Test Execution

### TC-01: Scale to 200 portions
- **Precondition:** Recipe `mutti_bread_rolls` exists and is approved.  
- **Input:** `target = 200`  
- **Expected Result:** Flour → 9600g, Water → 6000g, Salt → 100g, Yeast → 300g, Sugar → 300g  
- **Actual Result:** (to be filled after testing)  
- **Pass/Fail:** ⬜

### TC-02: Non‑linear scaling at 500 portions
- **Precondition:** Recipe has non‑linear rule for Salt (max 1.5× above 500).  
- **Input:** `target = 500`  
- **Expected Result:** Salt quantity = 7.5g (not 25g linear)  
- **Actual Result:** (to be filled after testing)  
- **Pass/Fail:** ⬜

### TC-03: Block ambiguous unit
- **Precondition:** Create a recipe with ingredient "pinch of salt".  
- **Input:** Try to mark recipe as Active.  
- **Expected Result:** System rejects activation and shows error.  
- **Actual Result:** (to be filled after testing)  
- **Pass/Fail:** ⬜

### TC-04: Unit normalisation
- **Precondition:** Conversion table has `cup = 240g`.  
- **Input:** Add ingredient "Flour: 2 cups".  
- **Expected Result:** Normalised grams = 480g.  
- **Actual Result:** (to be filled after testing)  
- **Pass/Fail:** ⬜

### TC-05: Rounding rules
- **Precondition:** Base recipe with 10 portions.  
- **Input:** Scale to 55 portions.  
- **Expected Result:** Quantities rounded to nearest 0.5g, 5g, or 10g as per rules.  
- **Actual Result:** (to be filled after testing)  
- **Pass/Fail:** ⬜

---

## 3. Defect Log

| Defect ID | Description | Severity | Status |
|-----------|-------------|----------|--------|
| D-01 | (to be filled if any) | – | – |

---

## 4. Final Decision

- [ ] **Accepted** – System meets all business requirements.
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