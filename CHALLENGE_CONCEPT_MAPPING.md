# Challenge-Concept Mapping

## Overview
This document maps existing challenges to concepts for the skill tree.

## Existing Challenges (41 total)

### Tutorial (Level 0)
- `hello_world` - Print "Hello, World!"
- `personal_greeting` - Personalized greeting with name
- `simple_math` - Basic arithmetic
- `favorite_things` - List favorites
- `name_length` - String length
- `temperature_converter` - Celsius/Fahrenheit conversion
- `mad_libs` - Text replacement game
- `guess_my_number` - Number guessing game

### Level 2 Intermediate
- `fizz_buzz` - Classic FizzBuzz
- `grade_calculator` - Calculate letter grades
- `password_validator` - Validate password strength
- `shopping_list` - Manage shopping items
- `todo_manager` - Task management
- `word_counter` - Count words in text

### Level 3 Intermediate
- `contact_book` - Contact management
- `custom_calculator` - Calculator with operations
- `data_processor` - Process data
- `error_handler` - Handle errors gracefully
- `file_analyzer` - Analyze file contents
- `inventory_system` - Game inventory

### Advanced
- `plugin_system` - Plugin architecture
- `context_manager` - Custom context managers
- `decorator_factory` - Decorator creation
- `property_validator` - Property validation
- `orm_lite` - Simple ORM
- `code_analyzer` - Code analysis
- `async_downloader` - Async downloads
- `config_parser` - Parse config files
- `test_suite` - Test writing
- `task_scheduler` - Task scheduling
- `container_add_exists` - Container operations

### Meta (Build LMSP)
10 meta challenges for building LMSP features

---

## Mapping: Concepts → Challenges

### Level 0 (Basics)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| print_function | hello_world | personal_greeting | - |
| variables | personal_greeting | simple_math | - |
| numbers | simple_math | - | - |
| basic_operators | simple_math | - | - |
| strings | personal_greeting | name_length | - |
| types | temperature_converter | - | - |
| comments | - | - | - |

### Level 1 (Control Flow)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| for_loops_basics | fizz_buzz | - | - |
| if_else | guess_my_number | grade_calculator | - |
| input_function | mad_libs | guess_my_number | - |
| match_case | - | - | - |
| type_conversion | temperature_converter | - | - |
| while_loops_basics | guess_my_number | - | - |

### Level 2 (Collections & Logic)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| boolean_logic | password_validator | - | - |
| dictionaries | contact_book | inventory_system | - |
| for_loops | fizz_buzz | - | - |
| if_elif_else | grade_calculator | - | - |
| in_operator | shopping_list | - | - |
| len_function | name_length | word_counter | - |
| list_comprehensions | - | - | - |
| lists | shopping_list | favorite_things | - |
| sets | - | - | - |
| sorted_function | - | - | - |
| string_methods | word_counter | - | - |
| tuples | - | - | - |
| while_loops | guess_my_number | - | - |

### Level 3 (Functions & Classes)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| classes | inventory_system | - | - |
| decorators | decorator_factory | - | - |
| def_return | custom_calculator | - | - |
| exceptions | error_handler | - | - |
| file_io | file_analyzer | - | - |
| functions | custom_calculator | - | - |
| imports | - | - | - |
| parameters | custom_calculator | - | - |
| scope | - | - | - |

### Level 4 (Intermediate Patterns)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| algorithms | - | - | - |
| comprehensions | - | - | - |
| context_managers | context_manager | - | - |
| dataclasses | - | - | - |
| generators | - | - | - |
| graphs_and_dags | - | - | - |
| integer_division | - | - | - |
| lambda | - | - | - |
| min_max_key | - | - | - |
| type_hints | - | - | - |

### Level 5 (Advanced)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| abstract_base_classes | plugin_system | - | - |
| async_await | async_downloader | - | - |
| context_vars | - | - | - |
| magic_methods | - | - | - |
| property_decorators | property_validator | - | - |
| protocols | - | - | - |
| pytest_basics | test_suite | - | - |

### Level 6 (Expert)
| Concept | Starter | Intermediate | Mastery |
|---------|---------|--------------|---------|
| descriptors | - | - | - |
| introspection | code_analyzer | - | - |
| metaclasses | orm_lite | - | - |
| pytest_fixtures | test_suite | - | - |

---

## Strategy

Many concepts have no matching challenges yet. The approach:
1. Map existing challenges where they fit
2. Leave empty strings for missing challenges (skill tree shows them as locked)
3. Future: Create missing challenges as needed

Challenges reused across multiple concepts is OK - learning the same concept in different contexts reinforces understanding.
