"""Pytest tests for Property Validator with Descriptors challenge."""
import subprocess
import sys

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestPropertyValidator:
    """Tests for the property validator descriptors challenge."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_code_runs(self, player_code: str):
        """Code should execute without runtime errors."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_has_required_classes(self, player_code: str):
        """Code should define all required descriptor classes."""
        required_classes = ["PositiveInt", "EmailStr", "RangeInt"]
        for cls in required_classes:
            assert f"class {cls}" in player_code, f"Define '{cls}' class"
        assert "def solution" in player_code, "Define a 'solution' function"

    def test_positive_int_valid(self, player_code: str):
        """PositiveInt should accept positive integers."""
        test_code = f'''
{player_code}

# Test PositiveInt with valid value
test_spec = {{"validator": "PositiveInt", "value": 42}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "valid" in stdout
        assert "42" in stdout

    def test_positive_int_invalid_negative(self, player_code: str):
        """PositiveInt should reject negative integers."""
        test_code = f'''
{player_code}

# Test PositiveInt with negative value
test_spec = {{"validator": "PositiveInt", "value": -5}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout
        assert "positive" in stdout.lower()

    def test_positive_int_invalid_zero(self, player_code: str):
        """PositiveInt should reject zero."""
        test_code = f'''
{player_code}

# Test PositiveInt with zero
test_spec = {{"validator": "PositiveInt", "value": 0}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout

    def test_email_valid(self, player_code: str):
        """EmailStr should accept valid email format."""
        test_code = f'''
{player_code}

# Test EmailStr with valid email
test_spec = {{"validator": "EmailStr", "value": "user@example.com"}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "valid" in stdout
        assert "user@example.com" in stdout

    def test_email_invalid_no_at(self, player_code: str):
        """EmailStr should reject email without @."""
        test_code = f'''
{player_code}

# Test EmailStr without @
test_spec = {{"validator": "EmailStr", "value": "invalidemail.com"}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout
        assert "@" in stdout

    def test_email_invalid_no_dot(self, player_code: str):
        """EmailStr should reject email without ."""
        test_code = f'''
{player_code}

# Test EmailStr without .
test_spec = {{"validator": "EmailStr", "value": "user@example"}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout
        assert "." in stdout

    def test_range_int_valid_in_range(self, player_code: str):
        """RangeInt should accept values within range."""
        test_code = f'''
{player_code}

# Test RangeInt with valid middle value
test_spec = {{"validator": "RangeInt", "min": 0, "max": 100, "value": 50}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "valid" in stdout
        assert "50" in stdout

    def test_range_int_valid_at_boundaries(self, player_code: str):
        """RangeInt should accept values at boundaries."""
        test_code = f'''
{player_code}

# Test RangeInt at min and max
test1 = solution({{"validator": "RangeInt", "min": 0, "max": 100, "value": 0}})
test2 = solution({{"validator": "RangeInt", "min": 0, "max": 100, "value": 100}})
print(f"min: {{test1['status']}}, max: {{test2['status']}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "min: valid" in stdout
        assert "max: valid" in stdout

    def test_range_int_invalid_below(self, player_code: str):
        """RangeInt should reject values below min."""
        test_code = f'''
{player_code}

# Test RangeInt below min
test_spec = {{"validator": "RangeInt", "min": 0, "max": 100, "value": -1}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout
        assert "0" in stdout or "100" in stdout

    def test_range_int_invalid_above(self, player_code: str):
        """RangeInt should reject values above max."""
        test_code = f'''
{player_code}

# Test RangeInt above max
test_spec = {{"validator": "RangeInt", "min": 0, "max": 100, "value": 101}}
result = solution(test_spec)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "invalid" in stdout

    def test_descriptor_protocol_implementation(self, player_code: str):
        """Descriptors should implement __get__ and __set__ methods."""
        test_code = f'''
{player_code}

# Test that descriptors implement required methods
has_get = "__get__" in player_code
has_set = "__set__" in player_code
has_set_name = "__set_name__" in player_code
print(f"__get__: {{has_get}}, __set__: {{has_set}}, __set_name__: {{has_set_name}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "__get__: True" in stdout
        assert "__set__: True" in stdout
        assert "__set_name__: True" in stdout

    def test_descriptor_reusability(self, player_code: str):
        """Descriptors should be reusable across multiple classes."""
        test_code = f'''
{player_code}

# Test descriptor reuse
class User:
    age = PositiveInt()
    email = EmailStr()

class Product:
    price = PositiveInt()  # Same descriptor, different class

user = User()
product = Product()

try:
    user.age = 25
    user.email = "test@example.com"
    product.price = 100
    print("reusable: yes", end="")
except:
    print("reusable: no", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "reusable: yes" in stdout
