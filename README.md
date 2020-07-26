# History Quiz Server Side Application
Uses [Google App Engine](en.wikipedia.org/wiki/Google_App_Engine) as platform to run application (cloud computing) and store entities in [Google Cloud Datastore](https://en.wikipedia.org/wiki/Google_Cloud_Datastore).

It is a `WSGIApplication` that handles:
1) Public api requests
2) Private maintenance requests (using simple html pages)
3) Cron jobs
