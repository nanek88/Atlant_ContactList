@AddNewUser
Feature: AddNewUser
# Feature Description: This test case will try to add new user to thinking tester contact list page

Scenario: Create new user
Given I get details for current user logged into the system and save details in UsersDetailsCache
And I add new user FName, LName with password test123 into the system and save details in NewUsersDetailsCache

Scenario: Add new contact to Contact List
Given I want to login as user using details from NewUsersDetailsCache with password test123 into the system and save details in LoggedUserDetailsCache
Then I want to add new contact with details: Name, Surname, 00387123456, Street 1, Street 2, City, Country, to Contact List and save details in AddedContactDetailsCache
Given I get details for contacts from Contact List and save details in ContactListDetailsCache
And Validate that contact from AddedContactDetailsCache is added to Contact List in ContactListDetailsCache
