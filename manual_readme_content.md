[comment]: # ""
[comment]: # "File: README.md"
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
