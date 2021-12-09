[comment]: # "Auto-generated SOAR connector documentation"
# Gigamon Application for Phantom

Publisher: Gigamon Inc\.  
Connector Version: 1\.0\.3  
Product Vendor: Gigamon Inc\.  
Product Name: Gigamon Application for Phantom  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 3\.0\.251  

This app leverages APIs from GigaVUE\-FM 5\.1 and above to perform investigative and corrective actions

[comment]: # ""
[comment]: # "File: readme.md"
[comment]: # ""
### EULA

Use of this app is subject to acceptance of the [Gigamon
EULA](https://www.gigamon.com/content/dam/resource-library/english/user---support-documentation/ms-eula-supplemental-terms-gimo-app-for-phantom.pdf)

### Modules

-   All modules in this app are packages as part of Python 2.7.4
-   This app uses the Python "requests" module when connecting to the GigaVUE-FM API
-   This app requires the json module for both Phantom specific code and converting GigaVUE-FM API
    output to a useable information
-   This app requires the time module to intiate the sleep command in the delete rule action

### Configuration notes

-   This App expects the API version of the GigaVUE FM to be v1.3. If any other version is in use
    the test connectivity and other actions will fail

### Playbook Notes

-   The Map Alias and ClusterId must be hard coded into any playbook actions to ensure proper
    functionality
-   The current actions are supported for first level maps

### Configuration Steps

-   Go to apps section, search for "Gigamon Application for Phantom" in search bar
-   The app will be under unconfigured apps, if configuring for the first time
-   Click "CONFIGURE NEW ASSET" and enter the configuration variables (refer section below)
-   Click "Save"
-   The app is configured to execute actions and run playbooks

### Support

-   For App support please contact: apps_support@gigamon.com


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Gigamon Application for Phantom asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**FM\_password** |  required  | password | GigaVUE FM password
**FM\_user** |  required  | string | GigaVUE FM Username
**FM\_server** |  required  | string | GigaVUE FM IP

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[get maps](#action-get-maps) - get a list of maps for a specific cluster id  
[get map](#action-get-map) - get a list of map rules for a specific map  
[post rule](#action-post-rule) - add a pass or drop rule to an existing map  
[delete rule](#action-delete-rule) - remove a rule from an existing map based on rule id  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get maps'
get a list of maps for a specific cluster id

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**cluster\_id** |  required  | Node IP/FQDN | string |  `cluster id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
action\_result\.parameter\.cluster\_id | string |  `cluster id` 
action\_result\.data\.\*\.maps\.\*\.alias | string |  `maps`   

## action: 'get map'
get a list of map rules for a specific map

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**cluster\_id** |  required  | Node IP/FQDN | string |  `cluster id` 
**map\_alias** |  required  | Name of the map to get | string |  `map alias` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.parameter\.map\_alias | string |  `map alias` 
action\_result\.data\.\*\.map\.rules\.\*\.\*\.alias | string |  `map alias` 
action\_result\.summary | string | 
action\_result\.parameter\.cluster\_id | string |  `cluster id` 
action\_result\.data\.\*\.map\.rules\.\*\.\*\.cluster\_id | string |  `cluster id` 
action\_result\.data\.\*\.map\.rules\.\*\.\*\.matches\.\*\.value | string | 
action\_result\.data\.\*\.map\.rules\.\*\.\*\.ruleid | string | 
action\_result\.data\.\*\.map\.rules\.\*\.\*\.rulecategory | string |   

## action: 'post rule'
add a pass or drop rule to an existing map

Type: **correct**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ipv4\_address** |  required  | address to add to the map | string | 
**rule\_type** |  required  | pass\|drop | string | 
**cluster\_id** |  required  | Node IP/FQDN | string |  `cluster id` 
**map\_alias** |  required  | Name of the map to add the rule to | string |  `map alias` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.data\.\*\.return\_code | string | 
action\_result\.parameter\.cluster\_id | string |  `cluster id` 
action\_result\.parameter\.map\_alias | string |  `map alias` 
action\_result\.parameter\.ipv4\_address | string | 
action\_result\.parameter\.rule\_type | string | 
action\_result\.summary | string |   

## action: 'delete rule'
remove a rule from an existing map based on rule id

Type: **correct**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**cluster\_id** |  required  | Node IP/FQDN | string |  `cluster id` 
**rule\_id** |  required  | ID of the rule to remove | string |  `rule id` 
**map\_alias** |  required  | Name of the map to remove the rule from | string |  `map alias` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.parameter\.cluster\_id | string |  `cluster id` 
action\_result\.parameter\.map\_alias | string |  `map alias` 
action\_result\.parameter\.rule\_id | string |  `rule id` 
action\_result\.data\.\*\.return\_code | string | 
action\_result\.summary | string | 