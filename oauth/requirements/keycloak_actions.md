# Keycloak Actions

## RealmRepresentation
  
| Name                                                                          | Type                                                                                  | Format |
|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|--------|
| **id**  <br>_optional_                                                        | String                                                                                |        |
| **realm**  <br>_optional_                                                     | String                                                                                |        |
| **displayName**  <br>_optional_                                               | String                                                                                |        |
| **displayNameHtml**  <br>_optional_                                           | String                                                                                |        |
| **notBefore**  <br>_optional_                                                 | Integer                                                                               | int32  |
| **defaultSignatureAlgorithm**  <br>_optional_                                 | String                                                                                |        |
| **revokeRefreshToken**  <br>_optional_                                        | Boolean                                                                               |        |
| **refreshTokenMaxReuse**  <br>_optional_                                      | Integer                                                                               | int32  |
| **accessTokenLifespan**  <br>_optional_                                       | Integer                                                                               | int32  |
| **accessTokenLifespanForImplicitFlow**  <br>_optional_                        | Integer                                                                               | int32  |
| **ssoSessionIdleTimeout**  <br>_optional_                                     | Integer                                                                               | int32  |
| **ssoSessionMaxLifespan**  <br>_optional_                                     | Integer                                                                               | int32  |
| **ssoSessionIdleTimeoutRememberMe**  <br>_optional_                           | Integer                                                                               | int32  |
| **ssoSessionMaxLifespanRememberMe**  <br>_optional_                           | Integer                                                                               | int32  |
| **offlineSessionIdleTimeout**  <br>_optional_                                 | Integer                                                                               | int32  |
| **offlineSessionMaxLifespanEnabled**  <br>_optional_                          | Boolean                                                                               |        |
| **offlineSessionMaxLifespan**  <br>_optional_                                 | Integer                                                                               | int32  |
| **clientSessionIdleTimeout**  <br>_optional_                                  | Integer                                                                               | int32  |
| **clientSessionMaxLifespan**  <br>_optional_                                  | Integer                                                                               | int32  |
| **clientOfflineSessionIdleTimeout**  <br>_optional_                           | Integer                                                                               | int32  |
| **clientOfflineSessionMaxLifespan**  <br>_optional_                           | Integer                                                                               | int32  |
| **accessCodeLifespan**  <br>_optional_                                        | Integer                                                                               | int32  |
| **accessCodeLifespanUserAction**  <br>_optional_                              | Integer                                                                               | int32  |
| **accessCodeLifespanLogin**  <br>_optional_                                   | Integer                                                                               | int32  |
| **actionTokenGeneratedByAdminLifespan**  <br>_optional_                       | Integer                                                                               | int32  |
| **actionTokenGeneratedByUserLifespan**  <br>_optional_                        | Integer                                                                               | int32  |
| **oauth2DeviceCodeLifespan**  <br>_optional_                                  | Integer                                                                               | int32  |
| **oauth2DevicePollingInterval**  <br>_optional_                               | Integer                                                                               | int32  |
| **enabled**  <br>_optional_                                                   | Boolean                                                                               |        |
| **sslRequired**  <br>_optional_                                               | String                                                                                |        |
| **passwordCredentialGrantAllowed**  <br>_optional_                            | Boolean                                                                               |        |
| **registrationAllowed**  <br>_optional_                                       | Boolean                                                                               |        |
| **registrationEmailAsUsername**  <br>_optional_                               | Boolean                                                                               |        |
| **rememberMe**  <br>_optional_                                                | Boolean                                                                               |        |
| **verifyEmail**  <br>_optional_                                               | Boolean                                                                               |        |
| **loginWithEmailAllowed**  <br>_optional_                                     | Boolean                                                                               |        |
| **duplicateEmailsAllowed**  <br>_optional_                                    | Boolean                                                                               |        |
| **resetPasswordAllowed**  <br>_optional_                                      | Boolean                                                                               |        |
| **editUsernameAllowed**  <br>_optional_                                       | Boolean                                                                               |        |
| **userCacheEnabled**  <br>_optional_                                          | Boolean                                                                               |        |
| **realmCacheEnabled**  <br>_optional_                                         | Boolean                                                                               |        |
| **bruteForceProtected**  <br>_optional_                                       | Boolean                                                                               |        |
| **permanentLockout**  <br>_optional_                                          | Boolean                                                                               |        |
| **maxFailureWaitSeconds**  <br>_optional_                                     | Integer                                                                               | int32  |
| **minimumQuickLoginWaitSeconds**  <br>_optional_                              | Integer                                                                               | int32  |
| **waitIncrementSeconds**  <br>_optional_                                      | Integer                                                                               | int32  |
| **quickLoginCheckMilliSeconds**  <br>_optional_                               | Long                                                                                  | int64  |
| **maxDeltaTimeSeconds**  <br>_optional_                                       | Integer                                                                               | int32  |
| **failureFactor**  <br>_optional_                                             | Integer                                                                               | int32  |
| **privateKey**  <br>_optional_                                                | String                                                                                |        |
| **publicKey**  <br>_optional_                                                 | String                                                                                |        |
| **certificate**  <br>_optional_                                               | String                                                                                |        |
| **codeSecret**  <br>_optional_                                                | String                                                                                |        |
| **roles**  <br>_optional_                                                     | RolesRepresentation                                                                   |        |
| **groups**  <br>_optional_                                                    | List of [GroupRepresentation](#GroupRepresentation)                                   |        |
| **defaultRoles**  <br>_optional_                                              | List of [\[string\]](#string)                                                         |        |
| **defaultRole**  <br>_optional_                                               | RoleRepresentation                                                                    |        |
| **defaultGroups**  <br>_optional_                                             | List of [\[string\]](#string)                                                         |        |
| **requiredCredentials**  <br>_optional_                                       | Set of [\[string\]](#string)                                                          |        |
| **passwordPolicy**  <br>_optional_                                            | String                                                                                |        |
| **otpPolicyType**  <br>_optional_                                             | String                                                                                |        |
| **otpPolicyAlgorithm**  <br>_optional_                                        | String                                                                                |        |
| **otpPolicyInitialCounter**  <br>_optional_                                   | Integer                                                                               | int32  |
| **otpPolicyDigits**  <br>_optional_                                           | Integer                                                                               | int32  |
| **otpPolicyLookAheadWindow**  <br>_optional_                                  | Integer                                                                               | int32  |
| **otpPolicyPeriod**  <br>_optional_                                           | Integer                                                                               | int32  |
| **otpPolicyCodeReusable**  <br>_optional_                                     | Boolean                                                                               |        |
| **otpSupportedApplications**  <br>_optional_                                  | List of [\[string\]](#string)                                                         |        |
| **webAuthnPolicyRpEntityName**  <br>_optional_                                | String                                                                                |        |
| **webAuthnPolicySignatureAlgorithms**  <br>_optional_                         | List of [\[string\]](#string)                                                         |        |
| **webAuthnPolicyRpId**  <br>_optional_                                        | String                                                                                |        |
| **webAuthnPolicyAttestationConveyancePreference**  <br>_optional_             | String                                                                                |        |
| **webAuthnPolicyAuthenticatorAttachment**  <br>_optional_                     | String                                                                                |        |
| **webAuthnPolicyRequireResidentKey**  <br>_optional_                          | String                                                                                |        |
| **webAuthnPolicyUserVerificationRequirement**  <br>_optional_                 | String                                                                                |        |
| **webAuthnPolicyCreateTimeout**  <br>_optional_                               | Integer                                                                               | int32  |
| **webAuthnPolicyAvoidSameAuthenticatorRegister**  <br>_optional_              | Boolean                                                                               |        |
| **webAuthnPolicyAcceptableAaguids**  <br>_optional_                           | List of [\[string\]](#string)                                                         |        |
| **webAuthnPolicyPasswordlessRpEntityName**  <br>_optional_                    | String                                                                                |        |
| **webAuthnPolicyPasswordlessSignatureAlgorithms**  <br>_optional_             | List of [\[string\]](#string)                                                         |        |
| **webAuthnPolicyPasswordlessRpId**  <br>_optional_                            | String                                                                                |        |
| **webAuthnPolicyPasswordlessAttestationConveyancePreference**  <br>_optional_ | String                                                                                |        |
| **webAuthnPolicyPasswordlessAuthenticatorAttachment**  <br>_optional_         | String                                                                                |        |
| **webAuthnPolicyPasswordlessRequireResidentKey**  <br>_optional_              | String                                                                                |        |
| **webAuthnPolicyPasswordlessUserVerificationRequirement**  <br>_optional_     | String                                                                                |        |
| **webAuthnPolicyPasswordlessCreateTimeout**  <br>_optional_                   | Integer                                                                               | int32  |
| **webAuthnPolicyPasswordlessAvoidSameAuthenticatorRegister**  <br>_optional_  | Boolean                                                                               |        |
| **webAuthnPolicyPasswordlessAcceptableAaguids**  <br>_optional_               | List of [\[string\]](#string)                                                         |        |
| **clientProfiles**  <br>_optional_                                            | List                                                                                  |        |
| **clientPolicies**  <br>_optional_                                            | List                                                                                  |        |
| **users**  <br>_optional_                                                     | List of [UserRepresentation](#UserRepresentation)                                     |        |
| **federatedUsers**  <br>_optional_                                            | List of [UserRepresentation](#UserRepresentation)                                     |        |
| **scopeMappings**  <br>_optional_                                             | List of [ScopeMappingRepresentation](#ScopeMappingRepresentation)                     |        |
| **clientScopeMappings**  <br>_optional_                                       | Map of [\[array\]](#array)                                                            |        |
| **clients**  <br>_optional_                                                   | List of [ClientRepresentation](#ClientRepresentation)                                 |        |
| **clientScopes**  <br>_optional_                                              | List of [ClientScopeRepresentation](#ClientScopeRepresentation)                       |        |
| **defaultDefaultClientScopes**  <br>_optional_                                | List of [\[string\]](#string)                                                         |        |
| **defaultOptionalClientScopes**  <br>_optional_                               | List of [\[string\]](#string)                                                         |        |
| **browserSecurityHeaders**  <br>_optional_                                    | Map of [\[string\]](#string)                                                          |        |
| **smtpServer**  <br>_optional_                                                | Map of [\[string\]](#string)                                                          |        |
| **userFederationProviders**  <br>_optional_                                   | List of [UserFederationProviderRepresentation](#UserFederationProviderRepresentation) |        |
| **userFederationMappers**  <br>_optional_                                     | List of [UserFederationMapperRepresentation](#UserFederationMapperRepresentation)     |        |
| **loginTheme**  <br>_optional_                                                | String                                                                                |        |
| **accountTheme**  <br>_optional_                                              | String                                                                                |        |
| **adminTheme**  <br>_optional_                                                | String                                                                                |        |
| **emailTheme**  <br>_optional_                                                | String                                                                                |        |
| **eventsEnabled**  <br>_optional_                                             | Boolean                                                                               |        |
| **eventsExpiration**  <br>_optional_                                          | Long                                                                                  | int64  |
| **eventsListeners**  <br>_optional_                                           | List of [\[string\]](#string)                                                         |        |
| **enabledEventTypes**  <br>_optional_                                         | List of [\[string\]](#string)                                                         |        |
| **adminEventsEnabled**  <br>_optional_                                        | Boolean                                                                               |        |
| **adminEventsDetailsEnabled**  <br>_optional_                                 | Boolean                                                                               |        |
| **identityProviders**  <br>_optional_                                         | List of [IdentityProviderRepresentation](#IdentityProviderRepresentation)             |        |
| **identityProviderMappers**  <br>_optional_                                   | List of [IdentityProviderMapperRepresentation](#IdentityProviderMapperRepresentation) |        |
| **protocolMappers**  <br>_optional_                                           | List of [ProtocolMapperRepresentation](#ProtocolMapperRepresentation)                 |        |
| **components**  <br>_optional_                                                | Map of [\[array\]](#array)                                                            |        |
| **internationalizationEnabled**  <br>_optional_                               | Boolean                                                                               |        |
| **supportedLocales**  <br>_optional_                                          | Set of [\[string\]](#string)                                                          |        |
| **defaultLocale**  <br>_optional_                                             | String                                                                                |        |
| **authenticationFlows**  <br>_optional_                                       | List of [AuthenticationFlowRepresentation](#AuthenticationFlowRepresentation)         |        |
| **authenticatorConfig**  <br>_optional_                                       | List of [AuthenticatorConfigRepresentation](#AuthenticatorConfigRepresentation)       |        |
| **requiredActions**  <br>_optional_                                           | List of [RequiredActionProviderRepresentation](#RequiredActionProviderRepresentation) |        |
| **browserFlow**  <br>_optional_                                               | String                                                                                |        |
| **registrationFlow**  <br>_optional_                                          | String                                                                                |        |
| **directGrantFlow**  <br>_optional_                                           | String                                                                                |        |
| **resetCredentialsFlow**  <br>_optional_                                      | String                                                                                |        |
| **clientAuthenticationFlow**  <br>_optional_                                  | String                                                                                |        |
| **dockerAuthenticationFlow**  <br>_optional_                                  | String                                                                                |        |
| **attributes**  <br>_optional_                                                | Map of [\[string\]](#string)                                                          |        |
| **keycloakVersion**  <br>_optional_                                           | String                                                                                |        |
| **userManagedAccessAllowed**  <br>_optional_                                  | Boolean                                                                               |        |
| **social**  <br>_optional_                                                    | Boolean                                                                               |        |
| **updateProfileOnInitialSocialLogin**  <br>_optional_                         | Boolean                                                                               |        |
| **socialProviders**  <br>_optional_                                           | Map of [\[string\]](#string)                                                          |        |
| **applicationScopeMappings**  <br>_optional_                                  | Map of [\[array\]](#array)                                                            |        |
| **applications**  <br>_optional_                                              | List of [ApplicationRepresentation](#ApplicationRepresentation)                       |        |
| **oauthClients**  <br>_optional_                                              | List of [OAuthClientRepresentation](#OAuthClientRepresentation)                       |        |
| **clientTemplates**  <br>_optional_                                           | List of [ClientTemplateRepresentation](#ClientTemplateRepresentation)                 |        |
| **oAuth2DeviceCodeLifespan**  <br>_optional_                                  | Integer                                                                               | int32  |
| **oAuth2DevicePollingInterval**  <br>_optional_                               | Integer                                                                               | int32  |


## ClientRepresentation
  
| Name                                                      | Type                                                                  | Format |
|-----------------------------------------------------------|-----------------------------------------------------------------------|--------|
| **id**  <br>_optional_                                    | String                                                                |        |
| **clientId**  <br>_optional_                              | String                                                                |        |
| **name**  <br>_optional_                                  | String                                                                |        |
| **description**  <br>_optional_                           | String                                                                |        |
| **rootUrl**  <br>_optional_                               | String                                                                |        |
| **adminUrl**  <br>_optional_                              | String                                                                |        |
| **baseUrl**  <br>_optional_                               | String                                                                |        |
| **surrogateAuthRequired**  <br>_optional_                 | Boolean                                                               |        |
| **enabled**  <br>_optional_                               | Boolean                                                               |        |
| **alwaysDisplayInConsole**  <br>_optional_                | Boolean                                                               |        |
| **clientAuthenticatorType**  <br>_optional_               | String                                                                |        |
| **secret**  <br>_optional_                                | String                                                                |        |
| **registrationAccessToken**  <br>_optional_               | String                                                                |        |
| **defaultRoles**  <br>_optional_                          | List of [\[string\]](#string)                                         |        |
| **redirectUris**  <br>_optional_                          | List of [\[string\]](#string)                                         |        |
| **webOrigins**  <br>_optional_                            | List of [\[string\]](#string)                                         |        |
| **notBefore**  <br>_optional_                             | Integer                                                               | int32  |
| **bearerOnly**  <br>_optional_                            | Boolean                                                               |        |
| **consentRequired**  <br>_optional_                       | Boolean                                                               |        |
| **standardFlowEnabled**  <br>_optional_                   | Boolean                                                               |        |
| **implicitFlowEnabled**  <br>_optional_                   | Boolean                                                               |        |
| **directAccessGrantsEnabled**  <br>_optional_             | Boolean                                                               |        |
| **serviceAccountsEnabled**  <br>_optional_                | Boolean                                                               |        |
| **oauth2DeviceAuthorizationGrantEnabled**  <br>_optional_ | Boolean                                                               |        |
| **authorizationServicesEnabled**  <br>_optional_          | Boolean                                                               |        |
| **directGrantsOnly**  <br>_optional_                      | Boolean                                                               |        |
| **publicClient**  <br>_optional_                          | Boolean                                                               |        |
| **frontchannelLogout**  <br>_optional_                    | Boolean                                                               |        |
| **protocol**  <br>_optional_                              | String                                                                |        |
| **attributes**  <br>_optional_                            | Map of [\[string\]](#string)                                          |        |
| **authenticationFlowBindingOverrides**  <br>_optional_    | Map of [\[string\]](#string)                                          |        |
| **fullScopeAllowed**  <br>_optional_                      | Boolean                                                               |        |
| **nodeReRegistrationTimeout**  <br>_optional_             | Integer                                                               | int32  |
| **registeredNodes**  <br>_optional_                       | Map of [\[integer\]](#integer)                                        | int32  |
| **protocolMappers**  <br>_optional_                       | List of [ProtocolMapperRepresentation](#ProtocolMapperRepresentation) |        |
| **clientTemplate**  <br>_optional_                        | String                                                                |        |
| **useTemplateConfig**  <br>_optional_                     | Boolean                                                               |        |
| **useTemplateScope**  <br>_optional_                      | Boolean                                                               |        |
| **useTemplateMappers**  <br>_optional_                    | Boolean                                                               |        |
| **defaultClientScopes**  <br>_optional_                   | List of [\[string\]](#string)                                         |        |
| **optionalClientScopes**  <br>_optional_                  | List of [\[string\]](#string)                                         |        |
| **authorizationSettings**  <br>_optional_                 | ResourceServerRepresentation                                          |        |
| **access**  <br>_optional_                                | Map of [\[boolean\]](#boolean)                                        |        |
| **origin**  <br>_optional_                                | String                                                                |        |

## UserRepresentation
  
| Name                                           | Type                                                                        | Format |
|------------------------------------------------|-----------------------------------------------------------------------------|--------|
| **self**  <br>_optional_                       | String                                                                      |        |
| **id**  <br>_optional_                         | String                                                                      |        |
| **origin**  <br>_optional_                     | String                                                                      |        |
| **createdTimestamp**  <br>_optional_           | Long                                                                        | int64  |
| **username**  <br>_optional_                   | String                                                                      |        |
| **enabled**  <br>_optional_                    | Boolean                                                                     |        |
| **totp**  <br>_optional_                       | Boolean                                                                     |        |
| **emailVerified**  <br>_optional_              | Boolean                                                                     |        |
| **firstName**  <br>_optional_                  | String                                                                      |        |
| **lastName**  <br>_optional_                   | String                                                                      |        |
| **email**  <br>_optional_                      | String                                                                      |        |
| **federationLink**  <br>_optional_             | String                                                                      |        |
| **serviceAccountClientId**  <br>_optional_     | String                                                                      |        |
| **attributes**  <br>_optional_                 | Map of [\[array\]](#array)                                                  |        |
| **credentials**  <br>_optional_                | List of [CredentialRepresentation](#CredentialRepresentation)               |        |
| **disableableCredentialTypes**  <br>_optional_ | Set of [\[string\]](#string)                                                |        |
| **requiredActions**  <br>_optional_            | List of [\[string\]](#string)                                               |        |
| **federatedIdentities**  <br>_optional_        | List of [FederatedIdentityRepresentation](#FederatedIdentityRepresentation) |        |
| **realmRoles**  <br>_optional_                 | List of [\[string\]](#string)                                               |        |
| **clientRoles**  <br>_optional_                | Map of [\[array\]](#array)                                                  |        |
| **clientConsents**  <br>_optional_             | List of [UserConsentRepresentation](#UserConsentRepresentation)             |        |
| **notBefore**  <br>_optional_                  | Integer                                                                     | int32  |
| **applicationRoles**  <br>_optional_           | Map of [\[array\]](#array)                                                  |        |
| **socialLinks**  <br>_optional_                | List of [SocialLinkRepresentation](#SocialLinkRepresentation)               |        |
| **groups**  <br>_optional_                     | List of [\[string\]](#string)                                               |        |
| **access**  <br>_optional_                     | Map of [\[boolean\]](#boolean)                                              |        |
| **userProfileMetadata**  <br>_optional_        | UserProfileMetadata                                                         |        |