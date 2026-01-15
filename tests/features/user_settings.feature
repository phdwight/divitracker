@user @settings
Feature: User Settings
    As a user
    I want to configure application settings
    So that I can customize currency and formatting

    Background:
        Given the application is configured for testing

    # Currency Settings
    Scenario: Create currency settings
        When I create currency settings with code "PHP" symbol "₱" and name "Philippine Peso"
        Then the currency code should be "PHP"
        And the currency symbol should be "₱"
        And the currency name should be "Philippine Peso"

    # Formatting Settings
    Scenario: Create formatting settings
        When I create formatting settings with thousands "," decimal "." and places 2
        Then the thousands separator should be ","
        And the decimal separator should be "."
        And the decimal places should be 2

    # Timezone Settings
    Scenario: Create timezone settings with positive offset
        When I create timezone settings with offset 8 and name "GMT+8"
        Then the timezone offset should be 8
        And the timezone name should be "GMT+8"

    Scenario: Create timezone settings with negative offset
        When I create timezone settings with offset -5 and name "EST"
        Then the timezone offset should be -5
        And the timezone name should be "EST"

    # Pagination Settings
    Scenario: Create pagination settings
        When I create pagination settings with 10 items per page
        Then the items per page should be 10

    Scenario: Create custom pagination settings
        When I create pagination settings with 25 items per page
        Then the items per page should be 25

    # User Settings Currency Formatting
    Scenario: Format currency with default PHP settings
        Given user settings with PHP currency
        When I format amount 1234.56
        Then the formatted result should be "₱1,234.56"

    Scenario: Format currency with zero
        Given user settings with PHP currency
        When I format amount 0
        Then the formatted result should be "₱0.00"

    Scenario: Format large currency amount
        Given user settings with PHP currency
        When I format amount 1000000
        Then the formatted result should be "₱1,000,000.00"

    Scenario: Format currency with USD settings
        Given user settings with USD currency
        When I format amount 1234.56
        Then the formatted result should be "$1,234.56"

    Scenario: Format currency with European settings
        Given user settings with EUR currency and European formatting
        When I format amount 1234.56
        Then the formatted result should be "€1 234,56"

    Scenario: Format currency with no decimal places
        Given user settings with JPY currency and no decimals
        When I format amount 1234
        Then the formatted result should be "¥1,234"

    # Settings Manager
    Scenario: Load default settings when no file exists
        Given no settings file exists
        When I load settings
        Then the currency code should be the default "PHP"
        And the currency symbol should be the default "₱"

    Scenario: Load settings from file
        Given a settings file with USD currency exists
        When I load settings
        Then the currency code should be "USD"
        And the currency symbol should be "$"

    Scenario: Save settings to file
        Given a new settings file path
        When I save EUR settings
        Then the file should contain currency code "EUR"
        And the file should contain currency symbol "€"

    Scenario: Reload settings from file
        Given a settings file with USD currency exists
        And the settings are loaded
        When the file is updated to EUR externally
        And I reload settings
        Then the currency code should be "EUR"

    Scenario: Partial settings merge with defaults
        Given a settings file with only currency defined
        When I load settings
        Then the currency should be from the file
        And the formatting should use defaults

    # Currency Presets
    Scenario: PHP preset exists
        Then the PHP preset should have code "PHP"
        And the PHP preset should have symbol "₱"
        And the PHP preset should have name "Philippine Peso"

    Scenario: Common currencies exist
        Then the preset "USD" should exist
        And the preset "EUR" should exist
        And the preset "GBP" should exist
        And the preset "JPY" should exist
        And the preset "CNY" should exist

    # Global Functions
    Scenario: Global format_currency function works
        When I use the global format_currency function with 1234.56
        Then the result should contain "₱"
        And the result should contain "1,234.56" or "1234.56"

    Scenario: Global get_user_settings function works
        When I use the global get_user_settings function
        Then the settings should be UserSettings type
        And the currency code should be "PHP"
