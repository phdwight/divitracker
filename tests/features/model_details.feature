@developer @models
Feature: Model Implementation Details
    As a developer
    I want the models to have proper representations and conversions
    So that debugging and API responses work correctly

    Background:
        Given the application is configured for testing

    # Dividend Frequency Enum
    Scenario: Monthly frequency has multiplier of 12
        Then the monthly frequency annual multiplier should be 12

    Scenario: Quarterly frequency has multiplier of 4
        Then the quarterly frequency annual multiplier should be 4

    Scenario: Yearly frequency has multiplier of 1
        Then the yearly frequency annual multiplier should be 1

    # Investment Representation
    Scenario: Investment with ticker has proper string representation
        Given an investment "Apple Inc" with ticker "AAPL" and 5000 dollars exists
        Then the investment repr should be "<Investment Apple Inc (AAPL)>"

    Scenario: Investment without ticker shows N/A in representation
        Given an investment "No Ticker Fund" without ticker and 5000 dollars exists
        Then the investment repr should be "<Investment No Ticker Fund (N/A)>"

    # Investment to_dict
    Scenario: Investment converts to dictionary correctly
        Given an investment "Dict Test" with ticker "DCT" and 1000 dollars exists
        When I convert the investment to a dictionary
        Then the dictionary should have name "Dict Test"
        And the dictionary should have ticker "DCT"
        And the dictionary should have total_invested 1000
        And the dictionary should have a created_at field

    # Investment Summary
    Scenario: Investment generates correct summary
        Given an investment "Summary Test" with ticker "SUM" and 10000 dollars exists
        And the investment has quarterly dividends of 100 dollars for the current year
        When I get the investment summary
        Then the summary total_invested should be 10000
        And the summary annual_dividends should be 400
        And the summary dividend_yield should be 4.0
        And the summary total_received should be 400

    # Dividend Representation
    Scenario: Dividend has proper string representation
        Given an investment "Div Rep Test" with ticker "DRT" and 5000 dollars exists
        And a dividend of 75.50 dollars with frequency "quarterly" exists for the investment
        Then the dividend repr should be "<Dividend $75.5 (quarterly)>"

    # Dividend to_dict
    Scenario: Dividend converts to dictionary correctly
        Given an investment "Div Dict Test" with ticker "DDT" and 5000 dollars exists
        And a dividend of 50 dollars with frequency "quarterly" and notes "Test note" exists for the investment
        When I convert the dividend to a dictionary
        Then the dividend dictionary should have amount 50
        And the dividend dictionary should have frequency "quarterly"
        And the dividend dictionary should have notes "Test note"
        And the dividend dictionary should have annualized_amount 200
        And the dividend dictionary should have investment_amount_at_time None
        And the dividend dictionary should have yield_at_time None

    Scenario: Dividend with investment amount converts to dictionary correctly
        Given an investment "Div Amt Test" with ticker "DAT" and 5000 dollars exists
        And a dividend of 50 dollars with frequency "quarterly" and investment balance 5000 exists for the investment
        When I convert the dividend to a dictionary
        Then the dividend dictionary should have investment_amount_at_time 5000
        And the dividend dictionary should have yield_at_time 4.0

    # Yield at time property
    Scenario: Yield at time calculates correctly for monthly dividend
        Given an investment "Yield Test" with ticker "YLD" and 10000 dollars exists
        And a dividend of 100 dollars with frequency "monthly" and investment balance 10000 exists for the investment
        Then the dividend yield_at_time should be 12.0

    Scenario: Yield at time is None when no investment amount
        Given an investment "No Amt Test" with ticker "NAT" and 5000 dollars exists
        And a dividend of 100 dollars with frequency "monthly" exists for the investment
        Then the dividend yield_at_time should be None

    Scenario: Yield at time is None when investment amount is zero
        Given an investment "Zero Amt Test" with ticker "ZAT" and 5000 dollars exists
        And a dividend of 100 dollars with frequency "monthly" and investment balance 0 exists for the investment
        Then the dividend yield_at_time should be None

    # Cascade Delete
    Scenario: Deleting investment deletes associated dividends
        Given an investment "Cascade Test" with ticker "CSC" and 1000 dollars exists
        And a dividend of 10 dollars with frequency "monthly" exists for the investment
        When I delete the investment "Cascade Test"
        Then the associated dividends should also be deleted
