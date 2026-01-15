@developer @utilities
Feature: Utility Functions
    As a developer
    I want utility functions to sanitize inputs
    So that the application is secure against injection attacks

    Background:
        Given the application is configured for testing

    # Sanitize Log Input (CWE-117 Prevention)
    Scenario: Normal string passes through unchanged
        When I sanitize "Hello World"
        Then the result should be "Hello World"

    Scenario: Newlines are escaped
        When I sanitize "Line1\nLine2"
        Then the result should be "Line1\\nLine2"

    Scenario: Carriage returns are escaped
        When I sanitize "Line1\rLine2"
        Then the result should be "Line1\\rLine2"

    Scenario: CRLF sequences are escaped
        When I sanitize "Line1\r\nLine2"
        Then the result should be "Line1\\r\\nLine2"

    Scenario: Control characters are removed
        When I sanitize a string with control characters
        Then the control characters should be removed

    Scenario: Tabs are preserved
        When I sanitize "Col1\tCol2"
        Then the result should be "Col1\tCol2"

    Scenario: Long strings are truncated
        When I sanitize a string of 300 characters
        Then the result should be 203 characters
        And the result should end with "..."

    Scenario: Non-string integer is converted
        When I sanitize integer 123
        Then the result should be "123"

    Scenario: None is converted to string
        When I sanitize None
        Then the result should be "None"

    Scenario: Empty string is handled
        When I sanitize ""
        Then the result should be ""

    Scenario: Log injection attempt is neutralized
        When I sanitize "Normal log\n2025-01-01 INFO Fake entry: Admin logged in"
        Then the result should not contain actual newline
        And the result should contain escaped newline "\\n"
