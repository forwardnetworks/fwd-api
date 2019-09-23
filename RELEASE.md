Release 0.0.25
========================
Improvements
------------------------
 * Fix missing slash in getting check endpoint

Release 0.0.24
========================
Improvements
------------------------
 * Add support for getting checks of a snapshot

Release 0.0.23
========================
Improvements
------------------------
 * Add check id to post check result

Release 0.0.22
========================
Improvements
------------------------
 * Add snapshot id to notification issues

Release 0.0.21
========================
Improvements
------------------------
 * Fix endpoint for getting notifications

Release 0.0.20
========================
Improvements
------------------------
 * Add support for getting notifications

Release 0.0.19
========================
Improvements
------------------------
 * Fix getting post check json result

Release 0.0.18
========================
Improvements
------------------------
 * Add support for returning post check result as Python class

Release 0.0.17
========================
Improvements
------------------------
 * Add support for getting result of posting check

Release 0.0.16
========================
Improvements
------------------------
 * Add support for filtering ICMP type in checks

Release 0.0.15
========================
Improvements
------------------------
 * Add support for direction field in PacketAliasFilter

Release 0.0.14
========================
Improvements
------------------------
 * Support TLS versions > 1.0
 * Add back support for network topology list file

Release 0.0.13
========================
Breaking changes
------------------------
 * Remove support for topology list file.
 * Handle collector status and upload data sources API changes.

Release 0.0.12
========================
Breaking changes
------------------------
### Rename of FromToClause to Clause
 * Use EndpointFilter instead of AndFilter when constructing checks.
 * Reachability check now requires EndpointFilter

Release 0.0.11
========================
Improvements
------------------------
 * Handle new collection status result server format introduced
   in version 2.15.0 of the VM.

Release 0.0.10
========================
Improvements
------------------------
 * Handle new collection status result server format introduced
   in version 2.10.0 of the VM


Release 0.0.9
========================
Improvements
------------------------
 * Adds support for getting devices and interfaces


Release 0.0.8
========================
Improvements
------------------------
 * A new traffic alias for VLANs


Release 0.0.7
========================
Improvements
------------------------
 * Preliminary support for searching flows


Release 0.0.6
========================

Improvements
------------------------
 * New IP-reachability check type
 * Support for "name" field in all checks

Breaking changes
------------------------
### Rename of FromToClause to Clause
 * Usages of NotFromToClause should be renamed to NotClause.
 * Usages of HostFromToClause should be renamed to HostClause.
 * Usages of AliasFromToClause should be renamed to AliasClause.

### Alias clause split
 * If referencing a HostAlias, usages of AliasClause should be renamed
   to HostAliasClause.
 * If referencing an InterfaceAlias or VlanInterfaceAlias, usages of
   AliasClause should be renamed to InterfaceAliasClause.
 * If referencing a TrafficAlias, IpV4TrafficAlias, etc., usages of
   AliasClause should be renamed to TrafficAliasClause.

### Change meaning of "ReachabilityCheck"
 * ReachabilityCheck now creates "Reachability" checks (full IP
   connectivity).
 * Use ExistenceCheck to create "Existential" checks (any
   connectivity).
