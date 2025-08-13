# OAuth Testing Suite

## Prerequisites

### Setting up automated application in Azure AD

In order to test the OAuth flow, you need to set up an application in Azure Active Directory (Azure AD) with the necessary permissions. Follow these steps:

1. Create an application in Azure AD
   - Go to Azure Portal > Azure Active Directory > App registrations > New registration.
   - Fill in the name, check `Accounts in this organizational directory only (Default Directory only - Single tenant)` and click `Register`.
2. In the application overview, navigate to API permissions.
   - Click `Add a permission`.
   - Select `Microsoft Graph` > `Delegated permissions`.
   - Add the following permissions:
     - User.ReadWrite.All 
     - Group.ReadWrite.All 
     - RoleManagement.ReadWrite.Directory 
     - AppRoleAssignment.ReadWrite.All 
     - Application.ReadWrite.All
   - Click `Add permissions`.
3. Click `Grant admin consent for <your tenant name>`.
4. Get back to overview and generate a client secret.
   - Navigate to `Certificates & secrets`.
   - Click `New client secret`, fill in the description and expiration, then click `Add`.
   - Copy the `value` of the client secret.