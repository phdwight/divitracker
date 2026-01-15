@user @investments
Feature: Investment Management
    As an investor
    I want to manage my investments
    So that I can track my portfolio

    Background:
        Given the application is configured for testing

    # Creating investments
    Scenario: Create a new investment
        Given no investments exist
        When I create an investment named "Apple Inc" with ticker "AAPL" and 5000 dollars
        Then the investment should be created successfully
        And the investment "Apple Inc" should have 5000 dollars invested

    Scenario: Add funds to an existing investment
        Given an investment "Tech Fund" with ticker "TECH" and 10000 dollars exists
        When I create an investment named "Tech Fund" with ticker "TECH" and 2000 dollars
        Then the investment "Tech Fund" should have 12000 dollars invested

    Scenario: Create investment without name fails
        When I try to create an investment with empty name and 1000 dollars
        Then I should see a validation error containing "required"

    Scenario: Create investment with invalid amount fails
        When I try to create an investment named "Test" with invalid amount "not_a_number"
        Then I should see a validation error containing "invalid"

    Scenario: Create investment with negative amount fails
        When I try to create an investment named "Test" with amount "-1000"
        Then I should see a validation error containing "negative"

    # Updating investments
    Scenario: Update investment details
        Given an investment "Old Name" with ticker "OLD" and 10000 dollars exists
        When I update the investment to name "New Name" ticker "NEW" and amount 15000
        Then the investment should be named "New Name"
        And the investment should have ticker "NEW"
        And the investment should have 15000 dollars invested

    # Deleting investments
    Scenario: Delete an investment
        Given an investment "To Delete" with ticker "DEL" and 5000 dollars exists
        When I delete the investment "To Delete"
        Then the investment "To Delete" should no longer exist

    Scenario: Delete non-existent investment fails
        When I try to delete an investment with ID 99999
        Then I should see a not found error

    # Viewing investments
    Scenario: View investment details
        Given an investment "My Fund" with ticker "FUND" and 25000 dollars exists
        When I view the investment "My Fund"
        Then I should see investment name "My Fund"
        And I should see ticker "FUND"
        And I should see total invested of 25000 dollars

    Scenario: List all investments
        Given an investment "Fund A" with ticker "FUNA" and 10000 dollars exists
        And an investment "Fund B" with ticker "FUNB" and 20000 dollars exists
        When I list all investments
        Then I should see 2 investments
        And I should see investment "Fund A" in the list
        And I should see investment "Fund B" in the list
