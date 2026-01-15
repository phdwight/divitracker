@admin
Feature: Admin Settings
    As an administrator
    I want to manage application settings
    So that I can customize the DiviTracker experience

    Background:
        Given the application is configured for testing

    # Admin Index
    Scenario: Admin index page renders
        When I visit "/settings/"
        Then I should see status code 200
        And I should see "Admin Settings" in the page

    Scenario: Admin index shows currency presets
        When I visit "/settings/"
        Then I should see "USD" in the page
        And I should see "EUR" in the page
        And I should see "PHP" in the page

    Scenario: Admin index shows current settings
        When I visit "/settings/"
        Then I should see "PHP" in the page

    Scenario: Admin index shows database section
        When I visit "/settings/"
        Then I should see "Database Management" in the page

    # Save Settings
    Scenario: Save settings successfully
        When I save settings with currency "USD" symbol "$" and name "US Dollar"
        Then I should see status code 200
        And the settings should be saved

    Scenario: Save settings with invalid decimal places
        When I save settings with decimal places "10"
        Then I should see "Decimal places must be between 0 and 4" in the page

    Scenario: Save settings with negative decimal places
        When I save settings with decimal places "-1"
        Then I should see "Decimal places must be between 0 and 4" in the page

    Scenario: Save settings with invalid timezone offset
        When I save settings with timezone offset "20"
        Then I should see "Timezone offset must be between -12 and +14" in the page

    # Database Download
    Scenario: Download database when file does not exist
        Given the database file does not exist
        When I request database download
        Then I should see "Database file not found" in the page

    Scenario: Download database successfully
        Given the database file exists with content "test database content"
        When I request database download
        Then I should receive file with content "test database content"
        And the content type should be "application/octet-stream"

    # Database Upload
    Scenario: Upload database without file
        When I upload database without file
        Then I should see "No file selected" in the page

    Scenario: Upload database with empty filename
        When I upload database with empty filename
        Then I should see "No file selected" in the page

    Scenario: Upload database with invalid extension
        When I upload database file "test.txt"
        Then I should see "Invalid file type" in the page

    Scenario: Upload database successfully
        Given the database file exists at temp path
        When I upload database file "backup.db" with content "new content"
        Then I should see "Database uploaded successfully" in the page
        And the database should contain "new content"

    Scenario: Upload database creates backup
        Given the database file exists with content "original content"
        When I upload database file "backup.db" with content "new content"
        Then a backup file should exist with content "original content"

    # Get DB Path
    Scenario: Get database path returns correct path
        When I get the database path
        Then the path should end with "dividends.db"
        And the path should contain "instance"
