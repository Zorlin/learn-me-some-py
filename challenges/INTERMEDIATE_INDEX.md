# LMSP Intermediate Challenges Index

Quick reference guide for Level 2-3 challenges.

## How to Use This Index

Each challenge is listed with:
- **Difficulty progression** (⭐ = easier, ⭐⭐⭐ = harder within level)
- **Time estimate** for average learner
- **Prerequisites** needed before attempting
- **What you'll build** in plain English

---

## Level 2: Collections & Basic Logic

### 1. FizzBuzz ⭐
**File:** `level_2_intermediate/fizz_buzz.toml`
**Time:** 5-10 minutes
**XP:** 25 points

**Prerequisites:**
- for loops
- if/elif statements
- modulo operator (%)

**What You'll Build:**
The classic coding interview problem. Generate a sequence where numbers divisible by 3 are "Fizz", by 5 are "Buzz", and by both are "FizzBuzz".

**Why This Matters:**
Famous problem that appears in interviews. Tests your understanding of logic order and remainder operations.

---

### 2. Shopping List Manager ⭐⭐
**File:** `level_2_intermediate/shopping_list.toml`
**Time:** 10-15 minutes
**XP:** 30 points

**Prerequisites:**
- Lists
- String .split()
- The 'in' operator

**What You'll Build:**
A shopping list app that can add items, remove items, check if items exist, count items, and display the full list.

**Why This Matters:**
Real app feature you'd use daily. Introduces command parsing and list operations.

---

### 3. Word Counter ⭐⭐
**File:** `level_2_intermediate/word_counter.toml`
**Time:** 10-20 minutes
**XP:** 35 points

**Prerequisites:**
- Dictionaries
- for loops
- .get() method

**What You'll Build:**
Count word frequencies in text and find the most common word. Like the basis of search engines!

**Why This Matters:**
First taste of data analysis. Dictionaries for counting is a fundamental pattern.

---

### 4. Password Validator ⭐⭐⭐
**File:** `level_2_intermediate/password_validator.toml`
**Time:** 15-25 minutes
**XP:** 40 points

**Prerequisites:**
- String methods (.isupper(), .islower(), .isdigit())
- any() function
- Complex boolean logic

**What You'll Build:**
Check if passwords are strong enough and give specific feedback on what's missing.

**Why This Matters:**
Real security code. Learn to validate user input properly.

---

### 5. TODO Manager ⭐⭐⭐
**File:** `level_2_intermediate/todo_manager.toml`
**Time:** 20-30 minutes
**XP:** 45 points

**Prerequisites:**
- Lists of dictionaries
- enumerate()
- String formatting

**What You'll Build:**
Full TODO app with task completion tracking, pending counts, and clearing completed tasks.

**Why This Matters:**
Complex state management. This is how real apps track data.

---

### 6. Grade Calculator ⭐⭐⭐
**File:** `level_2_intermediate/grade_calculator.toml`
**Time:** 20-35 minutes
**XP:** 50 points

**Prerequisites:**
- Dictionaries (nested)
- Weighted averages
- Multiple categories

**What You'll Build:**
Calculate student grades across categories with different weights. Convert to letter grades.

**Why This Matters:**
Math + programming. Weighted averages appear everywhere (scores, ratings, finances).

---

## Level 3: Functions, Classes & System Design

### 7. Contact Book Manager ⭐⭐
**File:** `level_3_intermediate/contact_book.toml`
**Time:** 20-30 minutes
**XP:** 50 points

**Prerequisites:**
- Functions
- Nested dictionaries
- Substring search

**What You'll Build:**
Contact manager with add, find, search, count, and delete operations.

**Why This Matters:**
First database-like system. Learn to organize structured data.

---

### 8. File Analyzer ⭐⭐
**File:** `level_3_intermediate/file_analyzer.toml`
**Time:** 20-30 minutes
**XP:** 50 points

**Prerequisites:**
- File I/O concepts
- String processing
- max() with key parameter

**What You'll Build:**
Analyze text files: count lines/words/chars, find longest word, find most frequent word.

**Why This Matters:**
Real data processing. Foundation for log analysis, text mining, search engines.

---

### 9. Error Handler ⭐⭐
**File:** `level_3_intermediate/error_handler.toml`
**Time:** 20-30 minutes
**XP:** 50 points

**Prerequisites:**
- try/except blocks
- Exception types (ValueError, ZeroDivisionError, KeyError)
- Defensive programming

**What You'll Build:**
Calculator that handles all errors gracefully and never crashes.

**Why This Matters:**
Professional code never crashes. Learn to anticipate and handle errors.

---

### 10. Custom Calculator Class ⭐⭐⭐
**File:** `level_3_intermediate/custom_calculator.toml`
**Time:** 25-40 minutes
**XP:** 50 points

**Prerequisites:**
- Classes and __init__
- self keyword
- Methods

**What You'll Build:**
Calculator class with memory storage and basic operations.

**Why This Matters:**
First object-oriented programming! Learn to think in classes and objects.

---

### 11. Inventory System ⭐⭐⭐
**File:** `level_3_intermediate/inventory_system.toml`
**Time:** 30-50 minutes
**XP:** 50 points

**Prerequisites:**
- Multiple classes
- Class interaction
- List comprehensions

**What You'll Build:**
Game inventory system with Item and Inventory classes working together.

**Why This Matters:**
Real game development pattern. Multiple objects working together.

---

### 12. Data Processor ⭐⭐⭐⭐
**File:** `level_3_intermediate/data_processor.toml`
**Time:** 30-50 minutes
**XP:** 50 points

**Prerequisites:**
- Function composition
- Dictionary mapping
- Pipeline pattern

**What You'll Build:**
Data processing pipeline that cleans, filters, transforms, and aggregates data.

**Why This Matters:**
Professional data engineering pattern. How real ETL systems work.

---

## Recommended Learning Paths

### Path 1: Practical Projects First
Perfect if you want to build useful stuff right away.

1. Shopping List Manager
2. TODO Manager
3. Password Validator
4. Contact Book Manager
5. Custom Calculator Class

### Path 2: Data Processing Track
Perfect if you love working with data and analysis.

1. Word Counter
2. Grade Calculator
3. File Analyzer
4. Data Processor

### Path 3: Computer Science Fundamentals
Perfect if you want the classic CS education path.

1. FizzBuzz
2. Password Validator
3. Error Handler
4. Custom Calculator Class
5. Inventory System

### Path 4: Game Development Focus
Perfect if you want to build games.

1. TODO Manager (for quest tracking)
2. Grade Calculator (for stats/XP systems)
3. Custom Calculator Class (for game state)
4. Inventory System (for RPG items)

---

## Difficulty Guide

**⭐ Easy** - Should take 5-15 minutes if you know the prerequisites
**⭐⭐ Medium** - 15-30 minutes, requires combining multiple concepts
**⭐⭐⭐ Hard** - 30-50 minutes, complex state or multiple moving parts
**⭐⭐⭐⭐ Very Hard** - 50+ minutes, professional-level patterns

---

## Tips for Success

### Before Starting a Challenge:
1. ✅ Read the full description
2. ✅ Check you've mastered the prerequisites
3. ✅ Look at the test cases to understand expected behavior
4. ✅ Start with the skeleton code provided

### While Coding:
1. 🎯 Run tests frequently (after every small change)
2. 🎯 Use hints if stuck for more than 5 minutes
3. 🎯 Start with the simplest test case first
4. 🎯 Don't hesitate to use gamepad hints if available

### After Completion:
1. 🎮 Press RT/LT to give emotional feedback
2. 🎮 Review the solution to see clean patterns
3. 🎮 Try to improve your time (speedrun!)
4. 🎮 Think about how this applies to real projects

---

## Emotional Checkpoints

Every challenge includes emotional feedback via controller triggers:

- **RT (Right Trigger)** - Pull to show enjoyment/satisfaction
- **LT (Left Trigger)** - Pull to show frustration/confusion
- **Y Button** - Press for complex/mixed feelings

This helps LMSP's adaptive AI learn YOUR learning style and adjust difficulty accordingly.

---

## Project Themes

Each challenge unlocks understanding for real-world projects:

| Challenge | Unlocks Understanding For |
|-----------|--------------------------|
| Shopping List | TODO apps, wishlists, inventory |
| Word Counter | Search engines, chat analysis, text mining |
| FizzBuzz | Game logic, pattern generation |
| Password Validator | Authentication, form validation, security |
| TODO Manager | Task trackers, project management, habit apps |
| Grade Calculator | Performance tracking, scoring systems |
| Contact Book | Address books, CRM systems, directories |
| File Analyzer | Log processing, text analysis, search |
| Error Handler | Robust APIs, input validation, safe operations |
| Custom Calculator | Game state, player stats, financial apps |
| Inventory System | RPG systems, store mechanics, asset tracking |
| Data Processor | ETL pipelines, data cleaning, batch jobs |

---

**Total XP Available:** 520 points
**Estimated Total Time:** 5-8 hours for complete mastery
**Completion Reward:** Ready for Level 4 (Advanced Python)!

Built with ❤️ in The Forge.
