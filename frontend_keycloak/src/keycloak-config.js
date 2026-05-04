// Keycloak-config.js

import Keycloak from "keycloak-js";



const initOptions = {
    url: "https://fireriskgroup02.com/auth/",
    realm: "frcm-realm",
    clientId: "frcm-react-app-client",
};



console.log("Keycloak Init Options:", initOptions); // Debugging line to check the config values

const keycloakConfig = new Keycloak(initOptions);


export default keycloakConfig;