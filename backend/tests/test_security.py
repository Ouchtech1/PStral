"""
Tests for security module.
"""
import pytest
from app.core.security import validate_prompt, filter_sql_prompt
from fastapi import HTTPException


class TestValidatePrompt:
    """Tests for prompt validation."""
    
    def test_safe_prompt_passes(self):
        """Test that safe prompts pass validation."""
        assert validate_prompt("SELECT * FROM users") == True
        assert validate_prompt("Show me all customers") == True
        assert validate_prompt("What is the total revenue?") == True
    
    def test_drop_keyword_blocked(self):
        """Test that DROP keyword is blocked."""
        with pytest.raises(HTTPException) as exc_info:
            validate_prompt("DROP TABLE users")
        assert exc_info.value.status_code == 400
        assert "DROP" in exc_info.value.detail
    
    def test_delete_keyword_blocked(self):
        """Test that DELETE keyword is blocked."""
        with pytest.raises(HTTPException) as exc_info:
            validate_prompt("DELETE FROM users WHERE id = 1")
        assert exc_info.value.status_code == 400
        assert "DELETE" in exc_info.value.detail
    
    def test_update_keyword_blocked(self):
        """Test that UPDATE keyword is blocked."""
        with pytest.raises(HTTPException) as exc_info:
            validate_prompt("UPDATE users SET name = 'hacker'")
        assert exc_info.value.status_code == 400
        assert "UPDATE" in exc_info.value.detail
    
    def test_truncate_keyword_blocked(self):
        """Test that TRUNCATE keyword is blocked."""
        with pytest.raises(HTTPException) as exc_info:
            validate_prompt("TRUNCATE TABLE users")
        assert exc_info.value.status_code == 400
        assert "TRUNCATE" in exc_info.value.detail
    
    def test_case_insensitive_blocking(self):
        """Test that keywords are blocked regardless of case."""
        with pytest.raises(HTTPException):
            validate_prompt("drop table users")
        with pytest.raises(HTTPException):
            validate_prompt("DrOp TaBlE users")


class TestFilterSQLPrompt:
    """Tests for SQL filtering."""
    
    def test_safe_select_passes(self):
        """Test that safe SELECT queries pass."""
        query = "SELECT * FROM employees WHERE department = 'IT'"
        result, reason = filter_sql_prompt(query)
        assert result == query
        assert reason is None
    
    def test_drop_blocked(self):
        """Test that DROP is blocked."""
        query = "DROP TABLE employees"
        result, reason = filter_sql_prompt(query)
        assert result == ""
        assert "DROP" in reason
    
    def test_semicolon_injection_blocked(self):
        """Test that semicolon comment injection is blocked."""
        query = "SELECT * FROM users; -- DROP TABLE users"
        result, reason = filter_sql_prompt(query)
        assert result == ""
        assert "injection" in reason.lower() or "multiple" in reason.lower()
    
    def test_union_injection_blocked(self):
        """Test that UNION injection is blocked."""
        query = "SELECT * FROM users UNION ALL SELECT * FROM passwords"
        result, reason = filter_sql_prompt(query)
        assert result == ""
        assert "injection" in reason.lower()
    
    def test_trailing_semicolon_removed(self):
        """Test that trailing semicolon is removed."""
        query = "SELECT * FROM users;"
        result, reason = filter_sql_prompt(query)
        assert result == "SELECT * FROM users"
        assert reason is None
    
    def test_multiple_statements_blocked(self):
        """Test that multiple statements are blocked."""
        query = "SELECT * FROM users; SELECT * FROM passwords"
        result, reason = filter_sql_prompt(query)
        assert result == ""
        assert "multiple" in reason.lower()

