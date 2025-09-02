# SRS-042 OAuth Authentication in ClickHouse
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Structure of OAuth](#structure-of-oauth)
* 2 [Definitions](#definitions)
* 3 [Overview of the Functionality](#overview-of-the-functionality)
    * 3.1 [Access Token Processors](#access-token-processors)
    * 3.2 [Authentication Modes with OAuth Tokens](#authentication-modes-with-oauth-tokens)
* 4 [Authentication with OAuth](#authentication-with-oauth)
    * 4.1 [Forward OAuth Identity](#forward-oauth-identity)
        * 4.1.1 [RQ.SRS-042.OAuth.Grafana.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaforwardoauthidentity)
* 5 [Identity Providers](#identity-providers)
    * 5.1 [Number of Identity Providers That Can Be Used Concurrently](#number-of-identity-providers-that-can-be-used-concurrently)
        * 5.1.1 [RQ.SRS-042.OAuth.IdentityProviders.Concurrent](#rqsrs-042oauthidentityprovidersconcurrent)
    * 5.2 [Changing Identity Providers](#changing-identity-providers)
        * 5.2.1 [RQ.SRS-042.OAuth.IdentityProviders.Change](#rqsrs-042oauthidentityproviderschange)
* 6 [Setting Up OAuth Authentication](#setting-up-oauth-authentication)
    * 6.1 [Credentials](#credentials)
        * 6.1.1 [RQ.SRS-042.OAuth.Credentials](#rqsrs-042oauthcredentials)
        * 6.1.2 [Access Token Processors are Missing From ClickHouse Configuration](#access-token-processors-are-missing-from-clickhouse-configuration)
            * 6.1.2.1 [RQ.SRS-042.OAuth.Authentication.UserRoles.NoAccessTokenProcessors](#rqsrs-042oauthauthenticationuserrolesnoaccesstokenprocessors)
    * 6.2 [External User Directory](#external-user-directory)
        * 6.2.1 [RQ.SRS-042.OAuth.Authentication.UserDirectories](#rqsrs-042oauthauthenticationuserdirectories)
            * 6.2.1.1 [Incorrect Configuration in User Directories](#incorrect-configuration-in-user-directories)
                * 6.2.1.1.1 [RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.provider](#rqsrs-042oauthauthenticationuserdirectoriesincorrectconfigurationprovider)
                * 6.2.1.1.2 [RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor](#rqsrs-042oauthauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenprocessor)
                * 6.2.1.1.3 [RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles](#rqsrs-042oauthauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenroles)
                * 6.2.1.1.4 [RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries](#rqsrs-042oauthauthenticationuserdirectoriesincorrectconfigurationtokenprocessorsmultipleentries)
            * 6.2.1.2 [Missing Configuration in User Directories](#missing-configuration-in-user-directories)
                * 6.2.1.2.1 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationaccesstokenprocessors)
                * 6.2.1.2.2 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationtokenprocessorsprovider)
                * 6.2.1.2.3 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationuserdirectories)
                * 6.2.1.2.4 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationuserdirectoriestoken)
                * 6.2.1.2.5 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenprocessor)
                * 6.2.1.2.6 [RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles](#rqsrs-042oauthauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenroles)
* 7 [Azure](#azure)
    * 7.1 [Setting up an Application in Azure](#setting-up-an-application-in-azure)
        * 7.1.1 [RQ.SRS-042.OAuth.Azure.ApplicationSetup](#rqsrs-042oauthazureapplicationsetup)
    * 7.2 [Support for Azure](#support-for-azure)
        * 7.2.1 [RQ.SRS-042.OAuth.Azure.Token.Supported](#rqsrs-042oauthazuretokensupported)
        * 7.2.2 [Token Constraints and Gateway Workaround For Azure](#token-constraints-and-gateway-workaround-for-azure)
            * 7.2.2.1 [RQ.SRS-042.OAuth.Azure.Tokens.Constraints](#rqsrs-042oauthazuretokensconstraints)
    * 7.3 [Getting Access Token from Azure](#getting-access-token-from-azure)
        * 7.3.1 [RQ.SRS-042.OAuth.Azure.GetAccessToken](#rqsrs-042oauthazuregetaccesstoken)
    * 7.4 [Access Token Processors For Azure](#access-token-processors-for-azure)
        * 7.4.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors](#rqsrs-042oauthidentityprovidersaccesstokenprocessors)
    * 7.5 [User Groups in Azure](#user-groups-in-azure)
        * 7.5.1 [Setting up User Groups in Azure](#setting-up-user-groups-in-azure)
            * 7.5.1.1 [RQ.SRS-042.OAuth.Authorization.Azure.UserDirectories.UserGroups](#rqsrs-042oauthauthorizationazureuserdirectoriesusergroups)
        * 7.5.2 [Query Execution Based on User Roles in ClickHouse with Azure](#query-execution-based-on-user-roles-in-clickhouse-with-azure)
            * 7.5.2.1 [RQ.SRS-042.OAuth.Authorization.Azure.UserRoles](#rqsrs-042oauthauthorizationazureuserroles)
        * 7.5.3 [Filtering Azure Groups for Role Assignment](#filtering-azure-groups-for-role-assignment)
            * 7.5.3.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.GroupFiltering](#rqsrs-042oauthazureauthenticationuserrolesgroupfiltering)
        * 7.5.4 [User in Multiple Azure Groups](#user-in-multiple-azure-groups)
            * 7.5.4.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.MultipleGroups](#rqsrs-042oauthazureauthenticationuserrolesmultiplegroups)
        * 7.5.5 [No Azure Groups Returned for User](#no-azure-groups-returned-for-user)
            * 7.5.5.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoGroups](#rqsrs-042oauthazureauthenticationuserrolesnogroups)
        * 7.5.6 [Azure Subgroup Memberships Not Considered](#azure-subgroup-memberships-not-considered)
            * 7.5.6.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.SubgroupMemberships](#rqsrs-042oauthazureauthenticationuserrolessubgroupmemberships)
        * 7.5.7 [Dynamic Group Membership Updates For Azure Users](#dynamic-group-membership-updates-for-azure-users)
            * 7.5.7.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.DynamicMembershipUpdates](#rqsrs-042oauthazureauthenticationuserrolesdynamicmembershipupdates)
        * 7.5.8 [Azure Group Names Match Roles in ClickHouse](#azure-group-names-match-roles-in-clickhouse)
            * 7.5.8.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.SameName](#rqsrs-042oauthazureauthenticationuserrolessamename)
        * 7.5.9 [No Matching Roles in ClickHouse for Azure Groups](#no-matching-roles-in-clickhouse-for-azure-groups)
            * 7.5.9.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthazureauthenticationuserrolesnomatchingroles)
        * 7.5.10 [User Cannot View Groups in Azure](#user-cannot-view-groups-in-azure)
            * 7.5.10.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthazureauthenticationuserrolesnopermissiontoviewgroups)
        * 7.5.11 [In ClickHouse There Is No Default Role Specified for Azure Users](#in-clickhouse-there-is-no-default-role-specified-for-azure-users)
            * 7.5.11.1 [RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthazureauthenticationuserrolesnodefaultrole)
    * 7.6 [Azure Identity Management Actions](#azure-identity-management-actions)
        * 7.6.1 [Azure User State Changes](#azure-user-state-changes)
            * 7.6.1.1 [RQ.SRS-042.OAuth.Azure.Actions.UserDisabled](#rqsrs-042oauthazureactionsuserdisabled)
            * 7.6.1.2 [RQ.SRS-042.OAuth.Azure.Actions.UserDeleted](#rqsrs-042oauthazureactionsuserdeleted)
            * 7.6.1.3 [RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset](#rqsrs-042oauthazureactionsuserpasswordreset)
        * 7.6.2 [Azure Group and Role Membership](#azure-group-and-role-membership)
            * 7.6.2.1 [RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup](#rqsrs-042oauthazureactionsuseraddedtogroup)
            * 7.6.2.2 [RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup](#rqsrs-042oauthazureactionsuserremovedfromgroup)
            * 7.6.2.3 [RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted](#rqsrs-042oauthazureactionsgroupdeleted)
        * 7.6.3 [Azure Application and Consent](#azure-application-and-consent)
            * 7.6.3.1 [RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled](#rqsrs-042oauthazureactionsapplicationdisabled)
            * 7.6.3.2 [RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved](#rqsrs-042oauthazureactionsadminconsentremoved)
            * 7.6.3.3 [RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated](#rqsrs-042oauthazureactionsclientsecretrotated)
        * 7.6.4 [Azure Token and Session Management](#azure-token-and-session-management)
            * 7.6.4.1 [RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked](#rqsrs-042oauthazureactionsusersessionrevoked)
* 8 [Keycloak](#keycloak)
    * 8.1 [Setting up a Realm in Keycloak](#setting-up-a-realm-in-keycloak)
        * 8.1.1 [RQ.SRS-042.OAuth.Keycloak.RealmSetup](#rqsrs-042oauthkeycloakrealmsetup)
    * 8.2 [Access Token Support for Keycloak](#access-token-support-for-keycloak)
        * 8.2.1 [RQ.SRS-042.OAuth.Keycloak.AccessTokenSupport](#rqsrs-042oauthkeycloakaccesstokensupport)
        * 8.2.2 [Access Token Constraints and Gateway Workaround For Keycloak](#access-token-constraints-and-gateway-workaround-for-keycloak)
            * 8.2.2.1 [RQ.SRS-042.OAuth.Keycloak.Tokens.OperationModes](#rqsrs-042oauthkeycloaktokensoperationmodes)
            * 8.2.2.2 [RQ.SRS-042.OAuth.Keycloak.Tokens.OperationModes.Fallback](#rqsrs-042oauthkeycloaktokensoperationmodesfallback)
            * 8.2.2.3 [RQ.SRS-042.OAuth.Keycloak.Tokens.Configuration.Validation](#rqsrs-042oauthkeycloaktokensconfigurationvalidation)
            * 8.2.2.4 [RQ.SRS-042.OAuth.Keycloak.Tokens.Operational.ProviderType](#rqsrs-042oauthkeycloaktokensoperationalprovidertype)
    * 8.3 [Getting Access Token from Keycloak](#getting-access-token-from-keycloak)
        * 8.3.1 [RQ.SRS-042.OAuth.Keycloak.GetAccessToken](#rqsrs-042oauthkeycloakgetaccesstoken)
    * 8.4 [Access Token Processors For Keycloak](#access-token-processors-for-keycloak)
        * 8.4.1 [RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors](#rqsrs-042oauthkeycloakaccesstokenprocessors)
    * 8.5 [User Groups in Keycloak](#user-groups-in-keycloak)
        * 8.5.1 [Setting up User Groups in Keycloak](#setting-up-user-groups-in-keycloak)
            * 8.5.1.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserDirectories.UserGroups](#rqsrs-042oauthkeycloakauthenticationuserdirectoriesusergroups)
        * 8.5.2 [Query Execution Based on User Roles in ClickHouse with Keycloak](#query-execution-based-on-user-roles-in-clickhouse-with-keycloak)
            * 8.5.2.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles](#rqsrs-042oauthkeycloakauthenticationuserroles)
        * 8.5.3 [Filtering Keycloak Groups for Role Assignment](#filtering-keycloak-groups-for-role-assignment)
            * 8.5.3.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.GroupFiltering](#rqsrs-042oauthkeycloakauthenticationuserrolesgroupfiltering)
        * 8.5.4 [User in Multiple Keycloak Groups](#user-in-multiple-keycloak-groups)
            * 8.5.4.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.MultipleGroups](#rqsrs-042oauthkeycloakauthenticationuserrolesmultiplegroups)
        * 8.5.5 [No Keycloak Groups Returned for User](#no-keycloak-groups-returned-for-user)
            * 8.5.5.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoGroups](#rqsrs-042oauthkeycloakauthenticationuserrolesnogroups)
        * 8.5.6 [Keycloak Subgroup Memberships Not Considered](#keycloak-subgroup-memberships-not-considered)
            * 8.5.6.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.SubgroupMemberships](#rqsrs-042oauthkeycloakauthenticationuserrolessubgroupmemberships)
        * 8.5.7 [Dynamic Group Membership Updates For Keycloak](#dynamic-group-membership-updates-for-keycloak)
            * 8.5.7.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles](#rqsrs-042oauthkeycloakauthenticationuserrolesnomatchingclickhouseroles)
        * 8.5.8 [Keycloak Group Names Match Roles in ClickHouse](#keycloak-group-names-match-roles-in-clickhouse)
            * 8.5.8.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.SameName](#rqsrs-042oauthkeycloakauthenticationuserrolessamename)
        * 8.5.9 [No Matching Roles in ClickHouse for Keycloak Groups](#no-matching-roles-in-clickhouse-for-keycloak-groups)
            * 8.5.9.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthkeycloakauthenticationuserrolesnomatchingroles)
        * 8.5.10 [User Cannot View Groups in Keycloak](#user-cannot-view-groups-in-keycloak)
            * 8.5.10.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthkeycloakauthenticationuserrolesnopermissiontoviewgroups)
        * 8.5.11 [In ClickHouse There Is No Default Role Specified for Keycloak Users](#in-clickhouse-there-is-no-default-role-specified-for-keycloak-users)
            * 8.5.11.1 [RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthkeycloakauthenticationuserrolesnodefaultrole)
    * 8.6 [Keycloak Identity Management Actions](#keycloak-identity-management-actions)
        * 8.6.1 [Keycloak User State Changes](#keycloak-user-state-changes)
            * 8.6.1.1 [RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled](#rqsrs-042oauthkeycloakactionsuserdisabled)
            * 8.6.1.2 [RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted](#rqsrs-042oauthkeycloakactionsuserdeleted)
        * 8.6.2 [Keycloak Group and Role Membership](#keycloak-group-and-role-membership)
            * 8.6.2.1 [RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup](#rqsrs-042oauthkeycloakactionsuseraddedtogroup)
            * 8.6.2.2 [RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup](#rqsrs-042oauthkeycloakactionsuserremovedfromgroup)
            * 8.6.2.3 [RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted](#rqsrs-042oauthkeycloakactionsgroupdeleted)
        * 8.6.3 [Keycloak Application and Consent](#keycloak-application-and-consent)
            * 8.6.3.1 [RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled](#rqsrs-042oauthkeycloakactionsclientdisabled)
            * 8.6.3.2 [RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked](#rqsrs-042oauthkeycloakactionsconsentrevoked)
        * 8.6.4 [Keycloak Token and Session Management](#keycloak-token-and-session-management)
            * 8.6.4.1 [RQ.SRS-042.OAuth.Keycloak.Actions.TokenInvalid](#rqsrs-042oauthkeycloakactionstokeninvalid)
* 9 [Static Key](#static-key)
    * 9.1 [Access Token Processors For Static Key](#access-token-processors-for-static-key)
        * 9.1.1 [RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors](#rqsrs-042oauthstatickeyaccesstokenprocessors)
    * 9.2 [Static Key as an External User Directory](#static-key-as-an-external-user-directory)
        * 9.2.1 [RQ.SRS-042.OAuth.StaticKey.UserDirectory](#rqsrs-042oauthstatickeyuserdirectory)
    * 9.3 [Static Key Algorithm Support](#static-key-algorithm-support)
        * 9.3.1 [RQ.SRS-042.OAuth.StaticKey.Algorithms](#rqsrs-042oauthstatickeyalgorithms)
            * 9.3.1.1 [RQ.SRS-042.OAuth.StaticKey.Algorithm.None](#rqsrs-042oauthstatickeyalgorithmnone)
    * 9.4 [Static Key Configuration Parameters](#static-key-configuration-parameters)
        * 9.4.1 [RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey](#rqsrs-042oauthstatickeyparametersstatickey)
        * 9.4.2 [RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64](#rqsrs-042oauthstatickeyparametersstatickeybase64)
        * 9.4.3 [RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey](#rqsrs-042oauthstatickeyparameterspublickey)
        * 9.4.4 [RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey](#rqsrs-042oauthstatickeyparametersprivatekey)
        * 9.4.5 [RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword](#rqsrs-042oauthstatickeyparameterspublickeypassword)
        * 9.4.6 [RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword](#rqsrs-042oauthstatickeyparametersprivatekeypassword)
        * 9.4.7 [RQ.SRS-042.OAuth.StaticKey.Parameters.Claims](#rqsrs-042oauthstatickeyparametersclaims)
    * 9.5 [Static Key Configuration Validation](#static-key-configuration-validation)
        * 9.5.1 [RQ.SRS-042.OAuth.StaticKey.Configuration.Validation](#rqsrs-042oauthstatickeyconfigurationvalidation)
* 10 [Static JWKS](#static-jwks)
    * 10.1 [Access Token Processors For Static JWKS](#access-token-processors-for-static-jwks)
        * 10.1.1 [RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors](#rqsrs-042oauthstaticjwksaccesstokenprocessors)
    * 10.2 [Static JWKS as an External User Directory](#static-jwks-as-an-external-user-directory)
        * 10.2.1 [RQ.SRS-042.OAuth.StaticJWKS.UserDirectory](#rqsrs-042oauthstaticjwksuserdirectory)
    * 10.3 [Static JWKS Configuration Parameters](#static-jwks-configuration-parameters)
        * 10.3.1 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks](#rqsrs-042oauthstaticjwksparametersstaticjwks)
        * 10.3.2 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile](#rqsrs-042oauthstaticjwksparametersstaticjwksfile)
        * 10.3.3 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims](#rqsrs-042oauthstaticjwksparametersclaims)
        * 10.3.4 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway](#rqsrs-042oauthstaticjwksparametersverifierleeway)
    * 10.4 [Static JWKS Configuration Validation](#static-jwks-configuration-validation)
        * 10.4.1 [RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation](#rqsrs-042oauthstaticjwksconfigurationvalidation)
    * 10.5 [Static JWKS Algorithm Support](#static-jwks-algorithm-support)
        * 10.5.1 [RQ.SRS-042.OAuth.StaticJWKS.Algorithms](#rqsrs-042oauthstaticjwksalgorithms)
* 11 [Remote JWKS](#remote-jwks)
    * 11.1 [Access Token Processors For Remote JWKS](#access-token-processors-for-remote-jwks)
        * 11.1.1 [RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors](#rqsrs-042oauthremotejwksaccesstokenprocessors)
    * 11.2 [Setting up Remote JWKS](#setting-up-remote-jwks)
        * 11.2.1 [RQ.SRS-042.OAuth.RemoteJWKS.Setup](#rqsrs-042oauthremotejwkssetup)
    * 11.3 [Remote JWKS Configuration Parameters](#remote-jwks-configuration-parameters)
        * 11.3.1 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri](#rqsrs-042oauthremotejwksparametersjwksuri)
        * 11.3.2 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout](#rqsrs-042oauthremotejwksparametersjwksrefreshtimeout)
        * 11.3.3 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims](#rqsrs-042oauthremotejwksparametersclaims)
        * 11.3.4 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway](#rqsrs-042oauthremotejwksparametersverifierleeway)
    * 11.4 [Remote JWKS Configuration Validation](#remote-jwks-configuration-validation)
        * 11.4.1 [RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation](#rqsrs-042oauthremotejwksconfigurationvalidation)
    * 11.5 [Remote JWKS Network Handling](#remote-jwks-network-handling)
        * 11.5.1 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout](#rqsrs-042oauthremotejwksnetworktimeout)
        * 11.5.2 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry](#rqsrs-042oauthremotejwksnetworkretry)
        * 11.5.3 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache](#rqsrs-042oauthremotejwksnetworkcache)
    * 11.6 [Remote JWKS Error Handling](#remote-jwks-error-handling)
        * 11.6.1 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure](#rqsrs-042oauthremotejwkserrorhandlingnetworkfailure)
        * 11.6.2 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse](#rqsrs-042oauthremotejwkserrorhandlinginvalidresponse)
        * 11.6.3 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache](#rqsrs-042oauthremotejwkserrorhandlingexpiredcache)
* 12 [Token Processor](#token-processor)
    * 12.1 [Common Configuration Parameters](#common-configuration-parameters)
        * 12.1.1 [RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime](#rqsrs-042oauthcommonparameterscachelifetime)
        * 12.1.2 [RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim](#rqsrs-042oauthcommonparametersusernameclaim)
        * 12.1.3 [RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim](#rqsrs-042oauthcommonparametersgroupsclaim)
        * 12.1.4 [RQ.SRS-042.OAuth.Common.Parameters.Unfiltered](#rqsrs-042oauthcommonparametersunfiltered)
    * 12.2 [Token Cache Behavior](#token-cache-behavior)
        * 12.2.1 [RQ.SRS-042.OAuth.Common.Cache.Behavior](#rqsrs-042oauthcommoncachebehavior)
    * 12.3 [Configuration Validation](#configuration-validation)
        * 12.3.1 [RQ.SRS-042.OAuth.Common.Configuration.Validation](#rqsrs-042oauthcommonconfigurationvalidation)
* 13 [ClickHouse Actions After Token Validation](#clickhouse-actions-after-token-validation)
    * 13.1 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
        * 13.1.1 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Alg](#rqsrs-042oauthauthenticationincorrectrequestsheaderalg)
        * 13.1.2 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Typ](#rqsrs-042oauthauthenticationincorrectrequestsheadertyp)
        * 13.1.3 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Signature](#rqsrs-042oauthauthenticationincorrectrequestsheadersignature)
        * 13.1.4 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Sub](#rqsrs-042oauthauthenticationincorrectrequestsbodysub)
        * 13.1.5 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Aud](#rqsrs-042oauthauthenticationincorrectrequestsbodyaud)
        * 13.1.6 [RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Exp](#rqsrs-042oauthauthenticationincorrectrequestsbodyexp)
    * 13.2 [Token Handling](#token-handling)
        * 13.2.1 [RQ.SRS-042.OAuth.Authentication.TokenHandling.Incorrect](#rqsrs-042oauthauthenticationtokenhandlingincorrect)
        * 13.2.2 [RQ.SRS-042.OAuth.Authentication.TokenHandling.EmptyString](#rqsrs-042oauthauthenticationtokenhandlingemptystring)
    * 13.3 [Caching](#caching)
        * 13.3.1 [RQ.SRS-042.OAuth.Authentication.Caching](#rqsrs-042oauthauthenticationcaching)
        * 13.3.2 [Disable Caching](#disable-caching)
            * 13.3.2.1 [RQ.SRS-042.OAuth.Authentication.Caching.CacheEviction.NoCache](#rqsrs-042oauthauthenticationcachingcacheevictionnocache)
        * 13.3.3 [Cache Lifetime](#cache-lifetime)
            * 13.3.3.1 [RQ.SRS-042.OAuth.Authentication.Caching.CacheEviction.CacheLifetime](#rqsrs-042oauthauthenticationcachingcacheevictioncachelifetime)
        * 13.3.4 [Cache Eviction Policy](#cache-eviction-policy)
            * 13.3.4.1 [RQ.SRS-042.OAuth.Authentication.Caching.TokensPerUser](#rqsrs-042oauthauthenticationcachingtokensperuser)
            * 13.3.4.2 [RQ.SRS-042.OAuth.Authentication.Caching.CacheEntryRefresh](#rqsrs-042oauthauthenticationcachingcacheentryrefresh)
            * 13.3.4.3 [RQ.SRS-042.OAuth.Authentication.Caching.LazyCleanup](#rqsrs-042oauthauthenticationcachinglazycleanup)
    * 13.4 [Authentication and Login](#authentication-and-login)
        * 13.4.1 [RQ.SRS-042.OAuth.Authentication.Actions.Authentication](#rqsrs-042oauthauthenticationactionsauthentication)
        * 13.4.2 [RQ.SRS-042.OAuth.Authentication.Actions.Authentication.Client](#rqsrs-042oauthauthenticationactionsauthenticationclient)

    
## Introduction

This Software Requirements Specification (SRS) defines the requirements for OAuth 2.0 authentication support in [ClickHouse].

OAuth 2.0 is an industry-standard authorization framework (defined in [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)) that enables third-party applications to obtain limited access to an HTTP service, either on behalf of a user or using application credentials. It decouples authentication from authorization, allowing for more secure and flexible access control mechanisms.

Integrating OAuth 2.0 in [ClickHouse] allows the system to delegate user authentication to trusted external identity providers (such as Google, Microsoft, or Okta), streamlining user management and enhancing security.

Through OAuth 2.0, [ClickHouse] can accept access tokens issued by an identity provider and validate them using static or dynamic JSON Web Key Sets (JWKS). The access token—typically a JWT—includes user identity and scope information that [ClickHouse] can use to authorize requests to resources.

This approach supports a wide range of identity federation use cases and enables [ClickHouse] to function within modern enterprise authentication ecosystems.

### Structure of OAuth

OAuth 2.0 defines several roles and token types used in the process of authorizing access to protected resources:

  * **Resource Owner:** The user or system that owns the data or resource.

  * **Client:** The application requesting access on behalf of the resource owner.
  * **Authorization Server:** The server that authenticates the resource owner and issues access tokens to the client.

  * **Resource Server:** The server (e.g., [ClickHouse]) that hosts the protected resources and verifies access tokens.

OAuth 2.0 typically issues two types of tokens:

  * **Access Token:** A short-lived token used by the client to access protected resources. In many implementations, the access token is a JWT that encodes user identity and scopes (permissions).

  * **Refresh Token:** An optional long-lived token used to obtain new access tokens without re-authenticating the user.

## Definitions

- **Identity Provider (IdP):** A service that issues access tokens after authenticating users. Examples include [Azure] Active Directory, Google Identity, and Okta.
- **Access Token:** A token issued by an IdP that grants access to protected resources. It is often a JSON Web Token (JWT) containing user identity and permissions, but in general its structure is provider-specific. 
- **[JWT (JSON Web Token)](https://github.com/Altinity/clickhouse-regression/blob/main/jwt_authentication/requirements/requirements.md):** A compact, URL-safe means of representing claims to be transferred between two parties. It can used in OAuth 2.0 for access tokens.
- [Grafana] User: A user in [Grafana] who can authenticate with [ClickHouse] using OAuth 2.0.
- [ClickHouse] User: A user defined in [ClickHouse] who can authenticate using OAuth 2.0 access tokens.
- **User Directory:** A source of user information that [ClickHouse] can query to retrieve user details and roles. This can be an external IdP or a locally defined user directory.
- User: A person or system that interacts with [ClickHouse] and can authenticate using OAuth 2.0 access tokens.

## Overview of the Functionality

To enable OAuth 2.0 authentication in [ClickHouse], one must define Access Token Processors, which allow [ClickHouse] to validate and trust OAuth 2.0 access tokens issued by external Identity Providers (IdPs), such as [Azure] AD.

OAuth-based authentication works by allowing users to authenticate using an access token issued by the IdP. [ClickHouse] supports two modes of operation with these tokens:

**Locally Defined Users:** If a user is already defined in [ClickHouse] (via `users.xml`), their authentication method can be set to jwt, enabling token-based authentication.

**Externally Defined Users:** If a user is not defined locally, [ClickHouse] can still authenticate and authorize them by validating the token and retrieving user information from the Identity Provider. If valid, the user is granted access with roles predefined in configuration and groups retrieved from IdP.

All OAuth 2.0 access tokens must be validated through one of the configured `token_processors` in `config.xml`.

### Access Token Processors

Key Parameters:

- **type:** Defines type of token processing workflow (acceptable values: `jwt`, `openid`, `azure`).

- **token_cache_lifetime:** maximum lifetime of cached token (in seconds). Optional, default: 3600

- **username_claim:** name of claim (field) that will be treated as ClickHouse username. Optional, default: "sub".

- **groups_claim:** Name of claim (field) that contains list of groups user belongs to. This claim will be looked up in the token itself (in case token is a valid JWT, e.g. in Keycloak) or in response from `/userinfo`. Optional, default: "groups".

### Authentication Modes with OAuth Tokens

1. **Locally Defined Users with JWT Authentication**
Users defined in `users.xml` can authenticate using tokens if `jwt` is specified as their method:

```xml
<clickhouse>
    <my_user>
        <jwt>
            <claims>{"resource_access":{"account": {"roles": ["view-profile"]}}}</claims>
        </jwt>
    </my_user>
</clickhouse>
```

`claims` is an optional parameter. If defined, presense of these claims in token is required, i.e. if a token is valid but does not have these claims - authentication will fail. 

2. **External Identity Provider as a User Directory**

When a user is not defined locally, [ClickHouse] can use the `IdP` as a dynamic source of user info. This requires configuring the `<token>` section in `users_directories` and assigning roles:

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <type>azure</type>
            <token_cache_lifetime>60</token_cache_lifetime>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

## Authentication with OAuth

To authenticate with OAuth, an access token must be obtained from the identity provider and presented to [ClickHouse].

### Forward OAuth Identity

#### RQ.SRS-042.OAuth.Grafana.ForwardOAuthIdentity
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

<img width="1023" height="266" alt="Screenshot from 2025-07-28 16-12-02" src="https://github.com/user-attachments/assets/6c9f38f1-ceaf-480a-8ca4-6599968cbb61" />

## Identity Providers

[ClickHouse] SHALL support OAuth 2.0 authentication with various identity providers, including but not limited to:

- [Azure] Active Directory
- Google Identity
- OpenID-compatible providers (e.g. Keycloak)

### Number of Identity Providers That Can Be Used Concurrently

#### RQ.SRS-042.OAuth.IdentityProviders.Concurrent
version: 1.0

[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `token_processors` section of `config.xml`.

### Changing Identity Providers

#### RQ.SRS-042.OAuth.IdentityProviders.Change
version: 1.0

[ClickHouse] SHALL allow changing the identity provider by updating the `token_processors` section in the `config.xml` file. After changing the identity provider, [ClickHouse] SHALL require a restart to apply the new configuration.

## Setting Up OAuth Authentication

### Credentials

#### RQ.SRS-042.OAuth.Credentials
version: 1.0

[Grafana] SHALL redirect the user to the Identity Provider authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>ClientnTENANT_ID=<Tenant ID>ClientnCLIENT_SECRET=<Client Secret>Clientn" > .env
```

#### Access Token Processors are Missing From ClickHouse Configuration

##### RQ.SRS-042.OAuth.Authentication.UserRoles.NoAccessTokenProcessors
version: 1.0

When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the external user to authenticate and access resources.

### External User Directory

An `external user directory` in [ClickHouse] is a remote identity source (such as `LDAP`, `Kerberos`, or an `OAuth Identity Provider`)
used to authenticate and retrieve user information that is not defined locally in [ClickHouse]. When enabled, [ClickHouse] dynamically
validates user credentials and assigns roles based on data from this external system instead of relying solely on locally configured users.

#### RQ.SRS-042.OAuth.Authentication.UserDirectories
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use the external provider as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.

For example,

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <type>azure</type>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

##### Incorrect Configuration in User Directories

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.provider
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `token_processors` or `user_directories` sections contain multiple entries that are the same.

For example, if there are multiple `<azuure>` entries in the `token_processors` section or multiple `<token>` entries in the `user_directories` section with the same `processor` attribute.

##### Missing Configuration in User Directories

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles
version: 1.0

[ClickHouse] SHALL not allow the external user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.


## Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with [Azure] Active Directory ([Azure] AD) as an identity provider.

### Setting up an Application in Azure

#### RQ.SRS-042.OAuth.Azure.ApplicationSetup
version: 1.0

[ClickHouse] SHALL support integration with applications registered in [Azure] Active Directory. To set up an application in [Azure] for OAuth authentication, the following steps SHALL be performed:

```bash
ACCESS_TOKEN="<admin-access-token>"

curl -s -X POST "https://graph.microsoft.com/v1.0/applications" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "ClickHouse OAuth App",
    "signInAudience": "AzureADMyOrg",
    "web": {
      "redirectUris": ["http://localhost:3000/login/generic_oauth"]
    }
  }'
```

### Support for Azure

#### RQ.SRS-042.OAuth.Azure.Token.Supported
version: 1.0

[ClickHouse] SHALL support validating access tokens issued by [Azure] AD using an Access Token Processor. The processor SHALL be defined in `config.xml` as follows:

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <type>azure</type>
            <token_cache_lifetime>600</token_cache_lifetime>
            <username_claim>sub</username_claim>
            <groups_claim>groups</groups_claim>
        </azuure>
    </token_processors>
</clickhouse>
```

#### Token Constraints and Gateway Workaround For Azure

##### RQ.SRS-042.OAuth.Azure.Tokens.Constraints
version: 1.0

[ClickHouse] SHALL assume that Azure-issued access tokens are not JWTs, thus cannot be decoded and validated locally.

### Getting Access Token from Azure

#### RQ.SRS-042.OAuth.Azure.GetAccessToken
version: 1.0

To obtain an access token from [Azure] AD, you need to register an application in [Azure] AD and configure the necessary permissions. After that you must collect your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET`.

You can obtain an access token using the following command:

```bash
TENANT_ID="<tenant-guid>"
CLIENT_ID="<app-client-id>"
CLIENT_SECRET="<app-client-secret>"

curl -s -X POST "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "grant_type=client_credentials" \
  -d "scope=https://graph.microsoft.com/.default"
```

### Access Token Processors For Azure

#### RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors
version: 1.0

An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token's issuer, audience, and cryptographic signature.

Basic structure:

```xml
<clickhouse>
    <token_processors>
        <azure_ad>
            <type>azure</type>
            <token_cache_lifetime>3600</token_cache_lifetime>
        </azure_ad>
    </token_processors>
</clickhouse>
```

### User Groups in Azure

#### Setting up User Groups in Azure

##### RQ.SRS-042.OAuth.Authorization.Azure.UserDirectories.UserGroups
version: 1.0

[ClickHouse] SHALL support user groups defined in [Azure] Active Directory ([Azure] AD) for role-based access control. In order to create a user group in [Azure] AD, you must obtain an [access token with the necessary permissions](#getting-access-token-from-azure) to create groups.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/groups" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "My App Users",
    "mailEnabled": false,
    "mailNickname": "myAppUsersNickname",
    "securityEnabled": true,
    "description": "Users allowed to access My App"
  }'
```

#### Query Execution Based on User Roles in ClickHouse with Azure

##### RQ.SRS-042.OAuth.Authorization.Azure.UserRoles
version: 1.0

When an external user is authenticated and authorized via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles described in the `users_directories` section.

Role mapping is based on the role name: if a user belongs to a group in [Azure] and there is a role with the same name in ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.

The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.

<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />


#### Filtering Azure Groups for Role Assignment

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.GroupFiltering
version: 1.0

When an external user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the [Azure] based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.

For example,

```xml
<clickhouse>
    <user_directories>
        <token>
            <processor>processor_name</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

The regex pattern `\bclickhouse-[a-zA-Z0-9]+\b` filters [Azure] AD group names to only match those that:

* Begin with exactly "clickhouse-"
* Are followed by one or more alphanumeric characters
* Are complete words (not parts of larger words)

This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.

If the filter is not set, all roles will be matched.

#### User in Multiple Azure Groups

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.MultipleGroups
version: 1.0

When a user belongs to multiple groups in the [Azure], [ClickHouse] SHALL combine all roles that match these group names.
The user SHALL inherit the union of all permissions from these roles.

#### No Azure Groups Returned for User

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoGroups
version: 1.0

When an external user is authenticated via OAuth and [Azure] does not return any groups for the user,
[ClickHouse] SHALL assign only the default roles if they are specified in the `<common_roles>` section of the `<token>` configuration. If no default roles are specified, the user SHALL not be able to read or write anything after authentication.

#### Azure Subgroup Memberships Not Considered

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.SubgroupMemberships
version: 1.0

When a user belongs to subgroups in the [Azure], [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.

#### Dynamic Group Membership Updates For Azure Users

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.DynamicMembershipUpdates
version: 1.0

[ClickHouse] SHALL reflect changes in a user's group memberships from the [Azure] dynamically during the next token validation or cache refresh.
Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.

#### Azure Group Names Match Roles in ClickHouse

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

#### No Matching Roles in ClickHouse for Azure Groups

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign only the default roles if they are specified in the `<common_roles>` section of the `<token>` configuration.

#### User Cannot View Groups in Azure

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign only the default roles if they are specified in the `<common_roles>` section of the `<token>` configuration.

#### In ClickHouse There Is No Default Role Specified for Azure Users

##### RQ.SRS-042.OAuth.Azure.Authentication.UserRoles.NoDefaultRole
version: 1.0

When an external user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, no default roles will be assigned to the user.

The role configuration example:

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <type>azure</type>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Azure Identity Management Actions

This section outlines how [ClickHouse] SHALL respond to various actions performed in [Azure] Active Directory that affect user identity, group membership, and token validity.

#### Azure User State Changes

##### RQ.SRS-042.OAuth.Azure.Actions.UserDisabled
version: 1.0

When a user is disabled in [Azure] AD, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens. However, [ClickHouse] MAY allow authentication in case there is a valid cache entry with the token. 

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/users/{user-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "accountEnabled": false
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserDeleted
version: 1.0

When a user is permanently deleted from [Azure] AD, [ClickHouse] SHALL reject any authentication attempts using their tokens. However, [ClickHouse] MAY allow authentication in case there is a valid cache entry with the token. 

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/users/{user-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset
version: 1.0

When a user's password is reset in [Azure] AD, [ClickHouse] SHALL continue to validate access tokens without interruption, as password changes do not invalidate existing tokens.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/authentication/passwordMethods/{method-id}/resetPassword" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "newPassword": "new-password"
  }'
```

#### Azure Group and Role Membership

##### RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup
version: 1.0

When a user is added to a group in [Azure] AD, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse]. However, in case there is a valid cache entry for the token, [ClickHouse] SHALL update user information only wafter the entry expires. 

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/groups/{group-id}/members/$ref" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{user-id}"
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup
version: 1.0

When a user is removed from a group in [Azure] AD, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login. However, in case there is a valid cache entry for the token, [ClickHouse] SHALL update user information only after the entry expires. 

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}/members/{user-id}/$ref" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted
version: 1.0

When a group that is mapped to a [ClickHouse] role is deleted in [Azure] AD, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication. However, in case there are valid cache entries for some users, [ClickHouse] SHALL update group information only after the entry expires. 

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Azure Application and Consent

##### RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled
version: 1.0

When the client application (service principal) used for OAuth integration is disabled in [Azure] AD, [ClickHouse] SHALL reject all incoming access tokens issued for that application. However, in case there are valid cache entreis for some users, [ClickHouse] SHALL allow them to authenticate until the corresponding entries expires. 

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "accountEnabled": false
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved
version: 1.0

If the admin consent for required permissions is revoked in [Azure] AD, [ClickHouse] SHALL reject authentication attempts until consent is granted again. However, in case there are valid cache entreis for some users, [ClickHouse] SHALL allow them to authenticate until the corresponding entries expires. 

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments/{assignment-id}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated
version: 1.0

When the client secret for the application is rotated in [Azure] AD, [ClickHouse] SHALL continue to validate tokens signed with the old secret until they expire, and seamlessly accept tokens signed with the new secret.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/applications/{app-id}/addPassword" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "passwordCredential": {
      "displayName": "New-Secret"
    }
  }'
```

#### Azure Token and Session Management

##### RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked
version: 1.0

When a user's sign-in sessions are revoked in [Azure] AD (for example, via the `revokeSignInSessions` API), [ClickHouse] SHALL reject the user's authentication attempts. However, in case there is a valid cache entry for some users, [ClickHouse] SHALL allow them to authenticate until the corresponding entries expires. 

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/revokeSignInSessions" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d ''
```

## Keycloak

[ClickHouse] SHALL support OAuth 2.0 authentication with Keycloak (or any other OpenID-compliant provider) as an external user directory.

### Setting up a Realm in Keycloak

#### RQ.SRS-042.OAuth.Keycloak.RealmSetup
version: 1.0

[ClickHouse] SHALL support integration with Keycloak realms. To set up a realm for OAuth authentication, the following steps SHALL be performed:

1. Prepare Realm Configuration JSON:

```json
{
  "realm": "grafana",
  "enabled": true,
  "clients": [
    {
      "clientId": "grafana-client",
      "name": "Grafana",
      "protocol": "openid-connect",
      "publicClient": false,
      "secret": "grafana-secret",
      "redirectUris": ["http://localhost:3000/login/generic_oauth"],
      "baseUrl": "http://localhost:3000",
      "standardFlowEnabled": true,
      "directAccessGrantsEnabled": true,
      "protocolMappers": [
        {
          "name": "groups",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-group-membership-mapper",
          "consentRequired": false,
          "config": {
            "claim.name": "groups",
            "jsonType.label": "String",
            "full.path": "false",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "userinfo.token.claim": "true"
          }
        }
      ]
    }
  ],
  "users": [
    {
      "username": "demo",
      "enabled": true,
      "email": "demo@example.com",
      "firstName": "Demo",
      "lastName": "User",
      "emailVerified": true,
      "groups": ["/grafana-admins", "/can-read"],
      "credentials": [
        {
          "type": "password",
          "value": "demo"
        }
      ]
    }
  ],
  "groups": [
    {
      "name": "grafana-admins",
      "path": "/grafana-admins"
    },
    {
      "name": "can-read",
      "path": "/can-read"
    }
  ]
}
```

2. Import Realm into Keycloak Docker Container:

```bash
docker run --name keycloak \
  -v $(pwd)/realm-export.json:/opt/keycloak/data/import/realm-export.json \
  quay.io/keycloak/keycloak:latest \
  start-dev --import-realm
```

### Access Token Support for Keycloak

#### RQ.SRS-042.OAuth.Keycloak.AccessTokenSupport
version: 1.0

[ClickHouse] SHALL support validating access access tokens issued by Keycloak using an Access Token Processor configured for OpenID. The processor SHALL be defined in config.xml as follows:

```xml
<clickhouse>
    <token_processors>
        <keycloak>
            <type>openid</type>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <token_cache_lifetime>600</token_cache_lifetime>
            <username_claim>sub</username_claim>
            <groups_claim>groups</groups_claim>
        </keycloak>
    </token_processors>
</clickhouse>
```

#### Access Token Constraints and Gateway Workaround For Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Tokens.OperationModes
version: 1.0

When <type>OpenID</type> is used (for Keycloak) in the `token_processors` section, [ClickHouse] SHALL 
validate tokens and extract user information by calling the configured discovery endpoint (`configuration_endpoint`) or `userinfo_endpoint` and `token_introspection_endpoint`.  

In some cases (i.e. when working with Keycloak) access tokens are JWTs, thus can be decoded and verified locally. If `jwks_uri` is specified / found in response from `configuration_endpoint` AND token is a JWT - [ClickHouse] SHALL attempt to validate the token locally against given JWKS.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.OperationModes.Fallback
version: 1.0

If attempt to validate token locally failed, [ClickHouse] SHALL fall back to processing the token using given user info and token introspection endpoints.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Configuration.Validation
version: 1.0

Exactly one of the following SHALL be configured per processor:

1. `configuration_endpoint`
2. both `userinfo_endpoint` and `token_introspection_endpoint`, and optionally `jwks_uri`.

If neither (or all three) are set, the configuration SHALL be rejected as invalid.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Operational.ProviderType
version: 1.0

To use Keycloak as provider, `type` SHALL be set to OpenID (case-insensitive). The processor SHALL obtain endpoints from the Keycloak 
realm's `.well-known/openid-configuration` or from explicitly provided `userinfo_endpoint` and `token_introspection_endpoint`.

### Getting Access Token from Keycloak

#### RQ.SRS-042.OAuth.Keycloak.GetAccessToken
version: 1.0

To obtain an access token from Keycloak, you need to have a configured realm, client, and user.

You can obtain an access token using the following command:

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxxx' \
  -d 'username=john' \
  -d 'password=secret'
```

### Access Token Processors For Keycloak

#### RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors
version: 1.0

An Access Token Processor for Keycloak defines how [ClickHouse] validates and interprets access tokens. This includes specifying the OpenID provider details.

Basic structure:

```xml
<clickhouse>
    <token_processors>
        <keycloak>
            <type>OpenID</type>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>
            <token_cache_lifetime>60</token_cache_lifetime>
        </keycloak>
    </token_processors>
</clickhouse>
```

### User Groups in Keycloak

#### Setting up User Groups in Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserDirectories.UserGroups
version: 1.0

[ClickHouse] SHALL support user groups defined in Keycloak for role-based access control. In order to create a user group in Keycloak, you must obtain an access token with the necessary permissions to create groups.

```bash
curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/groups' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "clickhouse-admin",
    "attributes": {
      "description": ["Users with administrative access to ClickHouse"]
    }
  }'
```

#### Query Execution Based on User Roles in ClickHouse with Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles
version: 1.0

When an external user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles 
assigned to the user in the `users_directories` section. Role mapping is based on the role name: 
if a user has a group or permission in Keycloak (or another IdP) and there is a role with the same name in
ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.

The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.

#### Filtering Keycloak Groups for Role Assignment

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.GroupFiltering
version: 1.0

When an external user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the `Keycloak` based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.

For example,

```xml
<clickhouse>
    <user_directories>
        <token>
            <processor>keycloak_processor</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

The regex pattern `\bclickhouse-[a-zA-Z0-9]+\b` filters Keycloak group names to only match those that:

* Begin with exactly "clickhouse-"
* Are followed by one or more alphanumeric characters
* Are complete words (not parts of larger words)

This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.

#### User in Multiple Keycloak Groups

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.MultipleGroups
version: 1.0

When a user belongs to multiple groups in the `Keycloak`, [ClickHouse] SHALL combine all roles that match these group names.
The user SHALL inherit the union of all permissions from these roles.

#### No Keycloak Groups Returned for User

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoGroups
version: 1.0

When an external user is authenticated via OAuth and Keycloak does not return any groups for the user,
[ClickHouse] SHALL assign only the default roles that are specified in the `<common_roles>` section of the `<token>` configuration. If no default roles are specified, the user SHALL NOT be able to read or write any data.

#### Keycloak Subgroup Memberships Not Considered

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.SubgroupMemberships
version: 1.0

When a user belongs to subgroups in the `Keycloak`, [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.

#### Dynamic Group Membership Updates For Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles
version: 1.0

[ClickHouse] SHALL reflect changes in a user's group memberships from the `Keycloak` dynamically during the next token validation or cache refresh.
Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.

#### Keycloak Group Names Match Roles in ClickHouse

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

#### No Matching Roles in ClickHouse for Keycloak Groups

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL only assign default roles (listed in `common_roles`) to the user.

#### User Cannot View Groups in Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL only assign default roles (listed in `common_roles`) to the user.

#### In ClickHouse There Is No Default Role Specified for Keycloak Users

##### RQ.SRS-042.OAuth.Keycloak.Authentication.UserRoles.NoDefaultRole
version: 1.0

When an external user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, no roles other than mapped from Keycloak groups shall be assigned to the user.

The role configuration example,

```xml
<clickhouse>
    <token_processors>
        <keycloak_processor>
            <type>OpenID</type>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>
        </keycloak_processor>
    </token_processors>
    <user_directories>
        <token>
            <processor>keycloak_processor</processor>
            <common_roles>
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Keycloak Identity Management Actions

This section outlines how [ClickHouse] SHALL respond to various actions performed in Keycloak that affect user identity, group membership, and token validity.

#### Keycloak User State Changes

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled
version: 1.0

When a user is disabled in Keycloak, [ClickHouse] SHALL reject any subsequent authentication attempts for that user. However, if [ClickHouse] has a valid token cache entry for the user, [ClickHouse] SHALL accept user authentication requests until the cache entry expires.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted
version: 1.0

When a user is permanently deleted from Keycloak, [ClickHouse] SHALL reject any authentication attempts using their tokens. However, if [ClickHouse] has a valid token cache entry for the user, [ClickHouse] SHALL accept user authentication requests until the cache entry expires.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Keycloak Group and Role Membership

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup
version: 1.0

When a user is added to a group in Keycloak, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse]. However, if [ClickHouse] has a valid token cache entry for the user, [ClickHouse] SHALL update role grants on the next authentication request after cache expires.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup
version: 1.0

When a user is removed from a group in Keycloak, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login. However, if [ClickHouse] has a valid token cache entry for the user, [ClickHouse] SHALL update role grants on the next authentication request after cache expires.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted
version: 1.0

When a group that is mapped to a [ClickHouse] role is deleted in Keycloak, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication. However, if [ClickHouse] has a valid token cache entry for the user, [ClickHouse] SHALL remove corresponding role grants on the next authentication request after cache expires.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Keycloak Application and Consent

##### RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled
version: 1.0

When the client application used for OAuth integration is disabled in Keycloak, [ClickHouse] SHALL reject all incoming access tokens issued for that client. However, if [ClickHouse] has a valid token cache entry for some of the users, [ClickHouse] SHALL accept authentication requests while corresponding cache entries are valid.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/clients/{client-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked
version: 1.0

If a user's consent for the application is revoked in Keycloak, [ClickHouse] SHALL reject authentication attempts until consent is granted again. However, if [ClickHouse] has a valid token cache entry for some of the users, [ClickHouse] SHALL accept authentication requests while corresponding cache entries are valid.
```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/consents/{client-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Keycloak Token and Session Management

##### RQ.SRS-042.OAuth.Keycloak.Actions.TokenInvalid
version: 1.0

If user's token becomes invalidated (for various reasons other than token expiration), [ClickHouse] SHALL reject authentication attempts with that token. However, if [ClickHouse] has a valid token cache entry for the corresponding user, [ClickHouse] SHALL accept authentication requests while corresponding cache entries are valid.

## Static Key

### Access Token Processors For Static Key

#### RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a static key. The configuration requires specifying the algorithm and the key.

```xml
<clickhouse>
    <token_processors>
        <my_static_key_validator>
          <type>jwt</type>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
        </my_static_key_validator>
    </token_processors>
</clickhouse>
```

### Static Key as an External User Directory

#### RQ.SRS-042.OAuth.StaticKey.UserDirectory
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static key as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.

```xml
<clickhouse>
    <token_processors>
        <my_static_key_validator>
          <type>jwt</type>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
        </my_static_key_validator>
    </token_processors>
    <user_directories>
        <token>
            <processor>my_static_key_validator</processor>
            <common_roles>
                <my_role />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Static Key Algorithm Support

#### RQ.SRS-042.OAuth.StaticKey.Algorithms
version: 1.0

[ClickHouse] SHALL support the following algorithms for static key validation:

| HMAC  | RSA   | ECDSA  | PSS   | EdDSA   |
|-------|-------|--------|-------|---------|
| HS256 | RS256 | ES256  | PS256 | Ed25519 |
| HS384 | RS384 | ES384  | PS384 | Ed448   |
| HS512 | RS512 | ES512  | PS512 |         |
|       |       | ES256K |       |         |

##### RQ.SRS-042.OAuth.StaticKey.Algorithm.None
version: 1.0

[ClickHouse] SHALL  support `None` algorithm.

### Static Key Configuration Parameters

#### RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey
version: 1.0

[ClickHouse] SHALL support the `static_key` parameter for symmetric algorithms (HS* family). This parameter SHALL be mandatory for `HS*` family algorithms and SHALL contain the secret key used for signature validation.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_hs256_validator>
            <type>jwt</type>
            <algo>HS256</algo>
            <static_key>my_secret_key_for_jwt_signing</static_key>
        </my_hs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64
version: 1.0

[ClickHouse] SHALL support the `static_key_in_base64` parameter to indicate if the `static_key` is base64-encoded. This parameter SHALL be optional with a default value of `False`.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_hs256_validator>
            <type>jwt</type>
            <algo>HS256</algo>
            <static_key>bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=</static_key>
            <static_key_in_base64>true</static_key_in_base64>
        </my_hs256_validator>
    </token_processors>
</clickhouse>
```

In this example, the base64-encoded string `bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=` decodes to `my_secret_key_for_jwt_signing`.

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey
version: 1.0

[ClickHouse] SHALL support the `public_key` parameter for asymmetric algorithms. This parameter SHALL be mandatory except for `HS*` family algorithms and `None` algorithm. The public key SHALL be used to verify JWT signatures.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey
version: 1.0

[ClickHouse] SHALL support the `private_key` parameter for asymmetric algorithms. This parameter SHALL be optional and SHALL be used when the private key is needed for additional operations.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
            <private_key>-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----</private_key>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword
version: 1.0

[ClickHouse] SHALL support the `public_key_password` parameter to specify the password for the public key. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <public_key>-----BEGIN ENCRYPTED PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END ENCRYPTED PUBLIC KEY-----</public_key>
            <public_key_password>my_public_key_password</public_key_password>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword
version: 1.0

[ClickHouse] SHALL support the `private_key_password` parameter to specify the password for the private key. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
            <private_key>-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END ENCRYPTED PRIVATE KEY-----</private_key>
            <private_key_password>my_private_key_password</private_key_password>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```


#### RQ.SRS-042.OAuth.StaticKey.Parameters.Claims
version: 1.0

[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <type>jwt</type>
            <algo>HS256</algo>
            <static_key>my_secret_key_for_jwt_signing</static_key>
            <claims>{"iss": "https://my-auth-server.com", "aud": "clickhouse-app"}</claims>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

### Static Key Configuration Validation

#### RQ.SRS-042.OAuth.StaticKey.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate static key configuration as follows:

* For `HS*` family algorithms: `static_key` SHALL be mandatory
* For asymmetric algorithms (RS*, ES*, PS*, Ed*): `public_key` SHALL be mandatory
* `algo` parameter SHALL be mandatory and SHALL contain a supported algorithm value
* If `static_key_in_base64` is `True`, [ClickHouse] SHALL decode the `static_key` from base64 before use

**Valid Configuration Examples:**

**HS256 with static key:**
```xml
<clickhouse>
    <token_processors>
        <hs256_validator>
            <type>jwt</type>
            <algo>HS256</algo>
            <static_key>my_secret_key</static_key>
        </hs256_validator>
    </token_processors>
</clickhouse>
```

**RS256 with public key:**
```xml
<clickhouse>
    <token_processors>
        <rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
        </rs256_validator>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Missing static_key for HS256:**
```xml
<clickhouse>
    <token_processors>
        <invalid_hs256_validator>
            <type>jwt</type>
            <algo>HS256</algo>
            <!-- Missing static_key - will be rejected -->
        </invalid_hs256_validator>
    </token_processors>
</clickhouse>
```

**Missing public_key for RS256:**
```xml
<clickhouse>
    <token_processors>
        <invalid_rs256_validator>
            <type>jwt</type>
            <algo>RS256</algo>
            <!-- Missing public_key - will be rejected -->
        </invalid_rs256_validator>
    </token_processors>
</clickhouse>
```


## Static JWKS

### Access Token Processors For Static JWKS

#### RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a static JSON Web Key Set (JWKS). The configuration can be provided directly or from a file.

```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
          <type>jwt</type>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

### Static JWKS as an External User Directory

#### RQ.SRS-042.OAuth.StaticJWKS.UserDirectory
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static JWKS as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.

```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
          <type>jwt</type>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
    <user_directories>
        <token>
            <processor>my_static_jwks_validator</processor>
            <common_roles>
                <my_role />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Static JWKS Configuration Parameters

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks
version: 1.0

[ClickHouse] SHALL support the `static_jwks` parameter to specify the JWKS content directly in JSON format. This parameter SHALL contain a valid JSON Web Key Set structure.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <type>jwt</type>
            <static_jwks>{
                "keys": [
                    {
                        "kty": "RSA",
                        "alg": "RS256",
                        "kid": "my-key-id-1",
                        "use": "sig",
                        "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
                        "e": "AQAB"
                    }
                ]
            }</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile
version: 1.0

[ClickHouse] SHALL support the `static_jwks_file` parameter to specify the path to a file containing the JWKS content. The file SHALL contain valid JSON Web Key Set data.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <type>jwt</type>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

**File content example (`/etc/clickhouse-server/jwks.json`):**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "my-key-id-1",
            "use": "sig",
            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
            "e": "AQAB"
        },
        {
            "kty": "RSA",
            "alg": "RS384",
            "kid": "my-key-id-2",
            "use": "sig",
            "n": "another-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims
version: 1.0

[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <type>jwt</type>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <claims>{"iss": "https://my-auth-server.com", "aud": "clickhouse-app"}</claims>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, tokens must contain both `iss` (issuer) and `aud` (audience) claims with the specified values to be considered valid.

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway
version: 1.0

[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <type>jwt</type>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <verifier_leeway>30</verifier_leeway>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, a 30-second clock skew tolerance is allowed, meaning tokens can be up to 30 seconds expired or not yet valid due to clock differences.

### Static JWKS Configuration Validation

#### RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate static JWKS configuration as follows:

* Only one of `static_jwks` or `static_jwks_file` SHALL be present in one verifier
* If both or neither are specified, [ClickHouse] SHALL reject the configuration as invalid
* Only RS* family algorithms SHALL be supported for static JWKS validation
* The JWKS content SHALL be valid JSON format
* If `static_jwks_file` is specified, the file SHALL exist and be readable

**Valid Configuration Examples:**

**Using static_jwks:**
```xml
<clickhouse>
    <token_processors>
        <valid_jwks_validator>
            <type>jwt</type>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </valid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Using static_jwks_file:**
```xml
<clickhouse>
    <token_processors>
        <valid_jwks_file_validator>
            <type>jwt</type>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
        </valid_jwks_file_validator>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Both static_jwks and static_jwks_file specified:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <type>jwt</type>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
            <!-- Both specified - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Neither static_jwks nor static_jwks_file specified:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <type>jwt</type>
            <!-- Neither specified - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Unsupported algorithm in JWKS:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <type>jwt</type>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "HS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <!-- HS256 not supported for JWKS - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

### Static JWKS Algorithm Support

#### RQ.SRS-042.OAuth.StaticJWKS.Algorithms
version: 1.0

[ClickHouse] SHALL support only RS* family algorithms for static JWKS validation:

* RS256
* RS384  
* RS512

[ClickHouse] SHALL reject JWKS entries with unsupported algorithms.

**Supported Algorithm Examples:**

**RS256:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "rs256-key",
            "use": "sig",
            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
            "e": "AQAB"
        }
    ]
}
```

**RS384:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS384",
            "kid": "rs384-key",
            "use": "sig",
            "n": "another-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

**RS512:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS512",
            "kid": "rs512-key",
            "use": "sig",
            "n": "third-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

**Unsupported Algorithm Example (will be rejected):**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "HS256",
            "kid": "hs256-key",
            "use": "sig",
            "n": "modulus-value",
            "e": "AQAB"
        }
    ]
}
```

## Remote JWKS

### Access Token Processors For Remote JWKS

#### RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a remote JSON Web Key Set (JWKS) fetched from a URI.

```xml
<clickhouse>
    <token_processors>
        <basic_auth_server>
          <type>jwt</type>
          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>
          <jwks_refresh_timeout>300</jwks_refresh_timeout>
        </basic_auth_server>
    </token_processors>
</clickhouse>
```

### Setting up Remote JWKS

#### RQ.SRS-042.OAuth.RemoteJWKS.Setup
version: 1.0

[ClickHouse] SHALL support custom JWKS setup for services that need to issue their own JWT tokens without using a full Identity Provider.

**Generate RSA Key Pair for JWT Signing:**

```bash
openssl genrsa -out jwt-private.pem 2048

openssl rsa -in jwt-private.pem -pubout -out jwt-public.pem
```

**Create JSON Web Key Set (JWKS) from Public Key:**

A JWKS is a JSON document that includes your public key parameters. For RSA it looks like:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "my-key-id-1",
      "use": "sig",
      "alg": "RS256",
      "n": "<base64url-modulus>",
      "e": "AQAB"
    }
  ]
}
```

**Deploy JWKS to HTTPS Web Server:**

Drop `jwks.json` behind any HTTPS-capable web server (nginx, Caddy, even a tiny Flask/FastAPI app). Example path:

```
https://auth.example.com/.well-known/jwks.json
```

**Configure ClickHouse Token Processor:**

```xml
<clickhouse>
  <token_processors>
    <my_service>
      <type>jwt</type>
      <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
      <jwks_refresh_timeout>300</jwks_refresh_timeout>
      <!-- Optional: claims / verifier_leeway -->
    </my_service>
  </token_processors>
</clickhouse>
```

**Sign JWT Tokens with Private Key:**

Your token issuer must:

* Sign with the matching private key (e.g., RS256)
* Include the same `kid` in the JWT header as in your JWKS entry
* (Optional) Include any claims you plan to enforce via ClickHouse's claims check

**Important Notes:**

* `kid` must match the `kid` you'll put in the JWT header when you sign tokens
* `n` and `e` are the RSA public key params, base64url-encoded
* You can generate that JSON with a tiny script using cryptography/pyjwt, or any JWK tool
* The specifics aren't ClickHouse-specific; ClickHouse only needs the public JWKS
* `jwks_uri`, `jwks_refresh_timeout`, `claims`, and `verifier_leeway` are exactly the supported params

### Remote JWKS Configuration Parameters

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri
version: 1.0

[ClickHouse] SHALL support the `jwks_uri` parameter to specify the JWKS endpoint URI. This parameter SHALL be mandatory and SHALL point to a valid JWKS endpoint.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>300</jwks_refresh_timeout>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

**Common JWKS endpoint patterns:**
* `https://auth.example.com/.well-known/jwks.json`
* `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys`
* `https://keycloak.example.com/realms/{realm}/protocol/openid-connect/certs`

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout
version: 1.0

[ClickHouse] SHALL support the `jwks_refresh_timeout` parameter to specify the period for resending requests to refresh the JWKS. This parameter SHALL be optional with a default value of 300 seconds.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>600</jwks_refresh_timeout>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, the JWKS will be refreshed every 10 minutes (600,000 milliseconds) instead of the default 5 minutes.

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims
version: 1.0

[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <claims>{"iss": "https://auth.example.com", "aud": "clickhouse-app", "azp": "clickhouse-client"}</claims>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, tokens must contain the specified `iss` (issuer), `aud` (audience), and `azp` (authorized party) claims to be considered valid.

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway
version: 1.0

[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <verifier_leeway>60</verifier_leeway>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, a 60-second clock skew tolerance is allowed, providing more flexibility for environments with larger clock synchronization issues.

### Remote JWKS Configuration Validation

#### RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate remote JWKS configuration as follows:

* `jwks_uri` parameter SHALL be mandatory and SHALL contain a valid URI
* The URI SHALL be accessible and return valid JWKS content
* If `jwks_refresh_timeout` is specified, it SHALL be a positive integer value
* [ClickHouse] SHALL validate the JWKS content format when fetched from the URI

**Valid Configuration Examples:**

**Basic configuration:**
```xml
<clickhouse>
    <token_processors>
        <valid_remote_jwks>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
        </valid_remote_jwks>
    </token_processors>
</clickhouse>
```

**With all optional parameters:**
```xml
<clickhouse>
    <token_processors>
        <complete_remote_jwks>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>600</jwks_refresh_timeout>
            <claims>{"iss": "https://auth.example.com"}</claims>
            <verifier_leeway>30</verifier_leeway>
        </complete_remote_jwks>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Missing jwks_uri:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <type>jwt</type>
            <!-- Missing jwks_uri - will be rejected -->
            <jwks_refresh_timeout>300</jwks_refresh_timeout>
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

**Invalid jwks_uri:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <type>jwt</type>
            <jwks_uri>not-a-valid-uri</jwks_uri>
            <!-- Invalid URI format - will be rejected -->
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

**Negative refresh timeout:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <type>jwt</type>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>-1000</jwks_refresh_timeout>
            <!-- Negative value - will be rejected -->
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

### Remote JWKS Network Handling

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout
version: 1.0

[ClickHouse] SHALL implement appropriate network timeouts when fetching JWKS from remote endpoints to prevent hanging requests.

**Example timeout scenarios:**
* Connection timeout: 10 seconds
* Read timeout: 30 seconds
* Total request timeout: 60 seconds

**Behavior:**
* If a JWKS fetch exceeds the timeout, [ClickHouse] SHALL log an error and continue using cached JWKS if available
* If no cached JWKS is available, authentication SHALL be rejected until the endpoint becomes accessible

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry
version: 1.0

[ClickHouse] SHALL implement retry logic for failed JWKS fetch attempts with exponential backoff to handle temporary network issues.

**Retry behavior:**
* Initial retry delay: 1 second
* Maximum retry delay: 60 seconds
* Maximum retry attempts: 3
* Exponential backoff: delay = min(initial_delay * 2^attempt, max_delay)

**Example retry sequence:**
1. First attempt fails → wait 1 second
2. Second attempt fails → wait 2 seconds  
3. Third attempt fails → wait 4 seconds
4. If all attempts fail, use cached JWKS or reject authentication

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache
version: 1.0

[ClickHouse] SHALL cache the fetched JWKS content for the duration specified by `jwks_refresh_timeout` to reduce network requests and improve performance.

**Caching behavior:**
* JWKS content SHALL be cached for the duration of `jwks_refresh_timeout`
* Cache SHALL be shared across all token validation requests
* Cache SHALL be refreshed in the background when the timeout expires
* If refresh fails, the old cached content SHALL continue to be used

**Example caching timeline:**
```
Time 0: Fetch JWKS from https://auth.example.com/.well-known/jwks.json
Time 0-300s: Use cached JWKS for all token validations
Time 300s: Background refresh attempt
Time 300s+: Use updated JWKS if refresh succeeded, or continue with old cache if failed
```

### Remote JWKS Error Handling

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure
version: 1.0

[ClickHouse] SHALL handle network failures when fetching JWKS gracefully. If the JWKS endpoint is unreachable, [ClickHouse] SHALL use cached JWKS if available, or reject authentication if no cached JWKS exists.

**Network failure scenarios:**
* DNS resolution failure
* Connection timeout
* HTTP 5xx server errors
* Network connectivity issues

**Example behavior:**
```
Scenario: JWKS endpoint https://auth.example.com/.well-known/jwks.json is down

1. First token validation: Use cached JWKS (if available)
2. Subsequent validations: Continue using cached JWKS
3. Background refresh attempts: Fail silently, keep using cache
4. If no cache exists: Reject all authentication attempts
5. When endpoint recovers: Resume normal operation
```

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse
version: 1.0

[ClickHouse] SHALL reject authentication attempts if the remote JWKS endpoint returns invalid or malformed JSON content.

**Invalid response scenarios:**
* Non-JSON content (HTML error pages, plain text)
* Malformed JSON syntax
* Missing required JWKS fields (`keys` array)
* Invalid key format within JWKS

**Example invalid responses:**

**HTML error page:**
```html
<!DOCTYPE html>
<html>
<head><title>500 Internal Server Error</title></head>
<body>Internal Server Error</body>
</html>
```

**Malformed JSON:**

```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "my-key",
            "n": "modulus",
            "e": "AQAB"
        }
    ]
```

Closing brace is missing, making it invalid JSON.

**Missing keys array:**
```json
{
    "error": "not_found",
    "error_description": "JWKS not available"
}
```

**Behavior:**
* [ClickHouse] SHALL log the invalid response for debugging
* Authentication SHALL be rejected for all tokens
* Cached JWKS SHALL not be used if the current response is invalid

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache
version: 1.0

[ClickHouse] SHALL attempt to refresh the JWKS cache when it expires. If the refresh fails, [ClickHouse] SHALL reject future authentication attempts.

**Cache expiration behavior:**
* When cache expires, [ClickHouse] SHALL attempt to fetch fresh JWKS
* If fetch succeeds: Use new JWKS immediately
* If fetch fails: Reject all authentication attempts

**Example timeline:**
```
Time 0: JWKS cached successfully
Time 300s: Cache expires, refresh attempt fails
Time 300+: Reject authentication if refresh still fails
```

**Graceful degradation:**
* This allows for temporary network issues without immediate service disruption
* Provides time for administrators to resolve connectivity problems
* Prevents indefinite use of potentially outdated keys

## Token Processor

### Common Configuration Parameters

#### RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime
version: 1.0

[ClickHouse] SHALL support the `token_cache_lifetime` parameter for all token processor types. This parameter SHALL specify the maximum lifetime of cached tokens in seconds. This parameter SHALL be optional with a default value of 3600 seconds.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <type>azure</type>
            <token_cache_lifetime>1800</token_cache_lifetime>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, tokens will be cached for 30 minutes (1800 seconds) instead of the default 1 hour.

#### RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim
version: 1.0

[ClickHouse] SHALL support the `username_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that will be treated as the ClickHouse username. This parameter SHALL be optional with a default value of "sub".

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <type>azure</type>
            <username_claim>preferred_username</username_claim>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, the `preferred_username` claim from the token will be used as the ClickHouse username instead of the default `sub` claim.

**Common username claim values:**
* `sub` (default) - Subject identifier
* `preferred_username` - User's preferred username
* `email` - User's email address
* `upn` - User Principal Name (Azure AD)
* `name` - User's display name

#### RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim
version: 1.0

[ClickHouse] SHALL support the `groups_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that contains the list of groups the user belongs to. This claim SHALL be looked up in the token itself (for valid JWTs) or in the response from `/userinfo` (for Non-JWTs). This parameter SHALL be optional with a default value of "groups".

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <type>azure</type>
            <groups_claim>roles</groups_claim>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, the `roles` claim from the token will be used to determine user groups instead of the default `groups` claim.

**Common groups claim values:**
* `groups` (default) - Standard groups claim
* `roles` - User roles
* `app_roles` - Application-specific roles
* `resource_access` - Resource access permissions
* `wids` - Windows Identity Foundation claims (Azure AD)

#### RQ.SRS-042.OAuth.Common.Parameters.Unfiltered
version: 1.0

[ClickHouse] SHALL reject a configuration inside `token_processors` that contains all possible parameters.

For example,

```xml
<clickhouse>
    <token_processors>
        <madness>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>
          <jwks_refresh_timeout>300</jwks_refresh_timeout>
          <type>openid</type>
          <token_cache_lifetime>600</token_cache_lifetime>
          <username_claim>sub</username_claim>
          <groups_claim>groups</groups_claim>
          <configuration_endpoint></configuration_endpoint>
          <userinfo_endpoint></userinfo_endpoint>
          <token_introspection_endpoint></token_introspection_endpoint>
        </madness>
    </token_processors>
</clickhouse>
```

### Token Cache Behavior

#### RQ.SRS-042.OAuth.Common.Cache.Behavior
version: 1.0

[ClickHouse] SHALL implement token caching behavior as follows:

* Tokens SHALL be cached internally for no longer than `token_cache_lifetime` seconds
* If a token expires sooner than `token_cache_lifetime`, the cache entry SHALL only be valid while the token is valid
* If a token lifetime is longer than `token_cache_lifetime`, the cache entry SHALL be valid for `token_cache_lifetime`
* Caching SHALL reduce the number of requests to Identity Providers

**Example caching scenarios:**

**Scenario 1: Token expires before token_cache_lifetime**
```
Token expiration: 30 minutes
Cache lifetime: 60 minutes
Result: Token cached for 30 minutes (until token expires)
```

**Scenario 2: Token expires after token_cache_lifetime**
```
Token expiration: 120 minutes
Cache lifetime: 60 minutes
Result: Token cached for 60 minutes (token_cache_lifetime limit)
```

**Scenario 3: Cache disabled**
```
Cache lifetime: 0
Result: No caching, validate token on every request
```

**Configuration example:**
```xml
<clickhouse>
    <token_processors>
        <my_processor>
            <type>azure</type>
            <token_cache_lifetime>1800</token_cache_lifetime>
        </my_processor>
    </token_processors>
</clickhouse>
```

**Cache behavior timeline:**
```
Time 0: Token received and validated
Time 0-1800s: Token cached, no validation requests to IdP
Time 1800s: Cache expires, next request triggers validation
Time 1800s+: New token cached for next 1800 seconds
```

### Configuration Validation

#### RQ.SRS-042.OAuth.Common.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate token processor configurations as follows:

* At least one token processor SHALL be defined in the `token_processors` section
* Each token processor SHALL have a unique name
* Required parameters for each processor type SHALL be present and valid
* [ClickHouse] SHALL reject invalid configurations and log appropriate error messages

**Valid Configuration Examples:**

**Multiple token processors:**
```xml
<clickhouse>
    <token_processors>
        <azure_processor>
            <type>azure</type>
        </azure_processor>
        <keycloak_processor>
            <type>openid</type>
            <userinfo_endpoint>https://keycloak.example.com/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>https://keycloak.example.com/introspect</token_introspection_endpoint>
        </keycloak_processor>
        <static_key_processor>
            <algo>HS256</algo>
            <static_key>my-secret-key</static_key>
        </static_key_processor>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**No token processors defined:**
```xml
<clickhouse>
    <token_processors>
        <!-- Empty section - will be rejected -->
    </token_processors>
</clickhouse>
```

**No token processors defined:**
```xml
<clickhouse>
    <token_processors>
        <algo>None</algo>
        <!-- `type` is not specified - will be rejected -->
    </token_processors>
</clickhouse>
```

**Duplicate processor identifiers:**
```xml
<clickhouse>
    <token_processors>
        <my_processor>
            <type>azure</type>
        </my_processor>
        <my_processor>
            <type>azure</type>
            <!-- Duplicate identifier - will be rejected -->
        </my_processor>
    </token_processors>
</clickhouse>
```

**Error handling:**
* [ClickHouse] SHALL log detailed error messages for configuration validation failures
* [ClickHouse] SHALL refuse to start if any token processor configuration is invalid
* Error messages SHALL include the specific parameter and reason for validation failure

## ClickHouse Actions After Token Validation

### Incorrect Requests to ClickHouse

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

#### RQ.SRS-042.OAuth.Authentication.IncorrectRequests.Body.Exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.

### Token Handling

#### RQ.SRS-042.OAuth.Authentication.TokenHandling.Incorrect
version: 1.0

[ClickHouse] SHALL reject JWT tokens that are malformed, have an invalid signature, or do not conform to the expected structure.

#### RQ.SRS-042.OAuth.Authentication.TokenHandling.EmptyString
version: 1.0

[ClickHouse] SHALL reject empty string values in the Authorization header or any other part of the request that expects a JWT token. An empty string is not a valid JWT and SHALL not be accepted.

### Caching

#### RQ.SRS-042.OAuth.Authentication.Caching
version: 1.0

[ClickHouse] SHALL cache the provided valid access token token for a configurable period of time to reduce the load on the Identity Provider. The cache lifetime SHALL be defined in the `token_processors` configuration.

For example,

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <type>azure</type>
            <token_cache_lifetime>60</token_cache_lifetime>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

In this case the cache will be valid for 60 seconds.

#### Disable Caching

##### RQ.SRS-042.OAuth.Authentication.Caching.CacheEviction.NoCache
version: 1.0

If the value of `token_cache_lifetime` is `0` in the `token_processors` configuration, [ClickHouse] SHALL not cache the tokens and SHALL validate each token on every request.

#### Cache Lifetime

##### RQ.SRS-042.OAuth.Authentication.Caching.CacheEviction.CacheLifetime
version: 1.0

[ClickHouse] SHALL evict cached tokens after the `token_cache_lifetime` period defined in the `token_processors` configuration. If the cache was evicted, [ClickHouse] SHALL cache the new token provided by user for the next requests.

#### Cache Eviction Policy

##### RQ.SRS-042.OAuth.Authentication.Caching.TokensPerUser
version: 1.0

[ClickHouse] SHALL store no more than one cache entry for each external user.

##### RQ.SRS-042.OAuth.Authentication.Caching.CacheEntryRefresh
version: 1.0

[ClickHouse] SHALL remove an existing cache entry for a user if the user successfully authenticated using another token. Old cache entry SHALL be removed even if old token / cache entry is still valid.

##### RQ.SRS-042.OAuth.Authentication.Caching.LazyCleanup
version: 1.0

[ClickHouse] SHALL NOT automatically remove expired cache entries. Cache entry will only be refreshed on user's next successful authentication.

### Authentication and Login

#### RQ.SRS-042.OAuth.Authentication.Actions.Authentication
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via `HTTP` or `TCP` connection.

For example,

```bash
curl 'http://localhost:8080/?' Client
 -H 'Authorization: Bearer <TOKEN>' Client
 -H 'Content type: text/plain;charset=UTF-8' Client
 --data-raw 'SELECT current_user()'
```

#### RQ.SRS-042.OAuth.Authentication.Actions.Authentication.Client
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an access token via the `clickhouse client --jwt <token>` command.

[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
[Keycloak]: https://www.keycloak.org
[Azure]: https://azure.microsoft.com
