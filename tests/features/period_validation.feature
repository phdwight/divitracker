@system @validation
Feature: Period Validation
    As a system
    I want to validate period month and year inputs
    So that dividend records have valid time periods

    Background:
        Given the application is configured for testing

    # Period Month Validation
    Scenario: Valid period months are accepted
        When I validate period month "1"
        Then the validated month should be 1
        When I validate period month "6"
        Then the validated month should be 6
        When I validate period month "12"
        Then the validated month should be 12

    Scenario: Empty or null period month returns None
        When I validate period month ""
        Then the validated month should be None
        When I validate period month with None
        Then the validated month should be None

    Scenario: Invalid period month string fails
        When I try to validate period month "invalid"
        Then I should see a validation error containing "invalid period month"

    Scenario: Period month 0 is out of range
        When I try to validate period month "0"
        Then I should see a validation error containing "between 1 and 12"

    Scenario: Period month 13 is out of range
        When I try to validate period month "13"
        Then I should see a validation error containing "between 1 and 12"

    # Period Year Validation
    Scenario: Valid period years are accepted
        When I validate period year "2025"
        Then the validated year should be 2025
        When I validate period year "1900"
        Then the validated year should be 1900
        When I validate period year "2100"
        Then the validated year should be 2100

    Scenario: Empty or null period year returns None
        When I validate period year ""
        Then the validated year should be None
        When I validate period year with None
        Then the validated year should be None

    Scenario: Invalid period year string fails
        When I try to validate period year "invalid"
        Then I should see a validation error containing "invalid period year"

    Scenario: Period year 1899 is out of range
        When I try to validate period year "1899"
        Then I should see a validation error containing "between 1900 and 2100"

    Scenario: Period year 2101 is out of range
        When I try to validate period year "2101"
        Then I should see a validation error containing "between 1900 and 2100"
