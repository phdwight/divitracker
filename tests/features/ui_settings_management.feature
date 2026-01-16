@admin @ui @settings
Feature: UI Settings Management
    As a user
    I want to configure application settings through the web interface
    So that I can customize the application to my preferences

    Background:
        Given the application is running

    Scenario: Navigate to settings page
        When I navigate to the dashboard
        And I click on the "Settings" link in navigation
        Then I should be on the "/settings/" page
        And I should see "Settings" heading

    Scenario: View currency settings
        When I navigate to "/settings/"
        Then I should see the currency selection dropdown
        And I should see available currency options
        And the current currency should be selected

    Scenario: Change currency
        When I navigate to "/settings/"
        And I select "USD" from the currency dropdown
        And I click the "Save Settings" button
        Then I should see a success message
        And the currency should be updated to "USD"

    Scenario: Configure decimal places
        When I navigate to "/settings/"
        And I enter "2" in the decimal places field
        And I click the "Save Settings" button
        Then I should see a success message
        And the decimal places should be set to 2

    Scenario: Configure thousands separator
        When I navigate to "/settings/"
        And I select "," as the thousands separator
        And I click the "Save Settings" button
        Then I should see a success message

    Scenario: Configure decimal separator
        When I navigate to "/settings/"
        And I select "." as the decimal separator
        And I click the "Save Settings" button
        Then I should see a success message

    Scenario: Configure pagination
        When I navigate to "/settings/"
        And I enter "20" in the items per page field
        And I click the "Save Settings" button
        Then I should see a success message
        And the default items per page should be 20

    Scenario: Configure timezone
        When I navigate to "/settings/"
        And I enter "8" in the timezone offset hours field
        And I enter "GMT+8" in the timezone name field
        And I click the "Save Settings" button
        Then I should see a success message
        And the timezone should be updated

    Scenario: View database backup section
        When I navigate to "/settings/"
        Then I should see the "Database Backup" section
        And I should see the "Download Backup" button
        And I should see the "Upload Backup" button

    Scenario: Download database backup
        When I navigate to "/settings/"
        And I click the "Download Backup" button for download
        Then a database file should be downloaded
        And the file should have a .db extension

    Scenario: Upload database backup
        Given I have a valid database backup file
        When I navigate to "/settings/"
        And I click the "Upload Backup" button
        And I select the backup file
        And I confirm the upload
        Then I should see a success message
        And the database should be restored

    Scenario: Validation - invalid decimal places
        When I navigate to "/settings/"
        And I enter "-1" in the decimal places field
        And I click the "Save Settings" button
        Then I should see a validation error

    Scenario: Validation - invalid pagination value
        When I navigate to "/settings/"
        And I enter "0" in the items per page field
        And I click the "Save Settings" button
        Then I should see a validation error

    Scenario: View all currency presets
        When I navigate to "/settings/"
        And I open the currency dropdown
        Then I should see "USD" option
        And I should see "EUR" option
        And I should see "GBP" option
        And I should see "JPY" option
        And I should see "PHP" option

    Scenario: Reset to default settings
        When I navigate to "/settings/"
        And I change multiple settings
        And I click the "Reset to Defaults" button if available
        Then the settings should return to default values

    Scenario: Settings persist across sessions
        When I navigate to "/settings/"
        And I select "EUR" from the currency dropdown
        And I click the "Save Settings" button
        And I navigate to the dashboard
        And I return to "/settings/"
        Then the currency should still be "EUR"
