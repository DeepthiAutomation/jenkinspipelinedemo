#!/bin/bash

# Prompt for username and password
read -p "Enter Cloud Foundry username: " USERNAME
read -s -p "Enter Cloud Foundry password: " PASSWORD
echo

# Function to bind, unbind, and restage an app
process_app() {
    local API_ENDPOINT=$1
    local APP_NAME=$2
    local ORG_NAME=$3
    local SPACE_NAME=$4

    # Login to Cloud Foundry
    echo "Logging into Cloud Foundry at $API_ENDPOINT..."
    cf login -a "$API_ENDPOINT" -u "$USERNAME" -p "$PASSWORD" -o "$ORG_NAME" -s "$SPACE_NAME"

    # Check if login was successful
    if [ $? -ne 0 ]; then
        echo "Failed to login to Cloud Foundry at $API_ENDPOINT."
        return
    fi

    # Select the organization and space
    echo "Targeting org $ORG_NAME and space $SPACE_NAME..."
    cf target -o "$ORG_NAME" -s "$SPACE_NAME"

    # Check if targeting was successful
    if [ $? -ne 0 ]; then
        echo "Failed to target org $ORG_NAME and space $SPACE_NAME."
        return
    fi

    # Bind the service (update SERVICE_INSTANCE with your actual service instance name)
    SERVICE_INSTANCE="your-service-instance"
    echo "Binding service $SERVICE_INSTANCE to app $APP_NAME..."
    cf bind-service "$APP_NAME" "$SERVICE_INSTANCE"

    # Check if binding was successful
    if [ $? -ne 0 ]; then
        echo "Failed to bind service $SERVICE_INSTANCE to app $APP_NAME."
        return
    fi

    # Unbind the service
    echo "Unbinding service $SERVICE_INSTANCE from app $APP_NAME..."
    cf unbind-service "$APP_NAME" "$SERVICE_INSTANCE"

    # Check if unbinding was successful
    if [ $? -ne 0 ]; then
        echo "Failed to unbind service $SERVICE_INSTANCE from app $APP_NAME."
        return
    fi

    # Restage the app
    echo "Restaging app $APP_NAME..."
    cf restage "$APP_NAME"

    # Check if restaging was successful
    if [ $? -ne 0 ]; then
        echo "Failed to restage app $APP_NAME."
        return
    fi

    echo "Completed bind, unbind, and restage operations successfully for $APP_NAME at $API_ENDPOINT."
}

# Read the CSV file and process each row
while IFS=, read -r API_ENDPOINT APP_NAME ORG_NAME SPACE_NAME; do
    # Skip the header row
    if [ "$API_ENDPOINT" != "API_ENDPOINT" ]; then
        process_app "$API_ENDPOINT" "$APP_NAME" "$ORG_NAME" "$SPACE_NAME"
    fi
done < input.csv
