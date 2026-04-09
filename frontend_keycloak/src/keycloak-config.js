// Keycloak-config.js

import Keycloak from "keycloak-js";



const initOptions = {
    url: process.env.REACT_APP_KEYCLOAK_URL,
    realm: process.env.REACT_APP_KEYCLOAK_REALM,
    clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID,
};




console.log("Keycloak Init Options:", initOptions); // Debugging line to check the config values

const keycloakConfig = new Keycloak(initOptions);


export default keycloakConfig;