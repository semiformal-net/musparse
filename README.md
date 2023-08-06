# Rss parsing and serving function

This pulls a [muspy](muspy.com) rss feed and applies filters before serving it back. It is deployed in google functions, but clients must be authenticated in order to access it.

## Secret

The code expects PARSE_URL environment variable which has to be set in google secret manager.

1. Enable [secretmanager API](https://console.cloud.google.com/flows/enableapi?apiid=secretmanager.googleapis.com) in the project

2. Go to [secret manager](https://console.cloud.google.com/security/secret-manager)

3. Enter a name like `PARSE_URL` and a value like `https://muspy.com/feed?id=abc123deadbeef`

## Set permissons for deploying the cloud function

```
PROJECT_ID=rssboxes-123456
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
# note that gen1 cloud functions use a different service account: PROJECT_ID@appspot.gserviceaccount.com
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \
    --role=roles/artifactregistry.reader
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor
```

## deploy the cloud function

Note that gen2 was causing errors (?) so I deploy gen1

```
#--ingress-settings=internal-only \
# --allow-unauthenticated \
gcloud functions deploy musparse \
--no-allow-unauthenticated \
--no-gen2 \
--region=northamerica-northeast1 \
--runtime=python311 \
--entry-point=main \
--set-secrets=PARSE_URL=PARSE_URL:1 \
--trigger-http
```

## set permission for app engine to call cloud function

This may not be required because i) we deploy with allow-unauthenticated (but with internal-only ingress) and because app engine uses the same service account as cloud function

```
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \
    --role=roles/cloudfunctions.invoker
```

## But this doesn't work

The only way to avoid authenticating to the function seems to be enabling `--allow-unauthenticated` and exposing the function to the whole world. `--ingress-settings=internal-only` does not work as expected since app engine is serverless and can have unpredictable IPs.

[This medium article](https://anushreesingh-36640.medium.com/invoking-http-google-cloud-function-from-google-app-engine-service-in-the-same-project-acd07fac1025) has details and steps to get a token to auth.
