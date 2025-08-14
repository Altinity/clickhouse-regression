# OAuth Testing Suite

## Setting up automated application in Azure AD

In order to test the OAuth flow, you need to set up an application in Azure Active Directory (Azure AD) with the necessary permissions. Follow these steps:

### Create an application in Azure AD
   - Go to Azure Portal > Azure Active Directory > App registrations > New registration.
   - Fill in the name, check `Accounts in this organizational directory only (Default Directory only - Single tenant)` and click `Register`.
  <img width="1842" height="729" alt="register_application_1" src="https://github.com/user-attachments/assets/95c88b88-680a-4077-a648-1dc41f50a0e9" />

### In the application overview, navigate to API permissions.
   - Click `Add a permission`.
   - Select `Microsoft Graph` > `Delegated permissions`.
   - Add the following permissions:
     - User.ReadWrite.All 
     - Group.ReadWrite.All 
     - RoleManagement.ReadWrite.Directory 
     - AppRoleAssignment.ReadWrite.All 
     - Application.ReadWrite.All
   - Click `Add permissions`.

<img width="797" height="258" alt="app_permissions_2" src="https://github.com/user-attachments/assets/3640d20e-c259-4b21-8a11-72fe55bbbf87" />

### Click `Grant admin consent for <your tenant name>`.
<img width="1294" height="498" alt="grant_permissions_3" src="https://github.com/user-attachments/assets/79439afb-f0d9-48db-a3fb-2336942d702e" />

### Get back to overview and generate a client secret.
   - Navigate to `Certificates & secrets`.
   - Click `New client secret`, fill in the description and expiration, then click `Add`.
   - Copy the `value` of the client secret.
<img width="2483" height="830" alt="client_secret_4" src="https://github.com/user-attachments/assets/49fdc648-2825-4b07-a244-f868653198f1" />
