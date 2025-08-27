Confluence page here: https://vbrick.atlassian.net/wiki/spaces/MQ/pages/1237417986/Embed+testing+tool

This tool takes in an iframe, constructs an HTML page with it, and uploads it to S3. Then it provides the URL to the page, and automatically opens the page in the browser of your choice.

## **One-Time Setup**

1. Create a file with the AWS credentials (found on this page: [S3 Browser settings for QA Cloud](https://vbrick.atlassian.net/wiki/x/G4aE)) \
   Format:

   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY`


2. Save the file on your machine in this folder:

   `C:\Users\<Your user name>\.aws\credentials`

   ex. `C:\Users\alex.mcIntosh\.aws`

Note: it’s hardcoded to upload the HTML page to the vb-alex S3 bucket which is configured with `public-read` permissions.\
https\://vb-alex.s3.us-east-1.amazonaws.com/embed\_previews/

---

## **How to Use**

1. Run `embed_viewer.exe`
2. Paste your iframe embed code (or press Enter to reuse the previous iframe).
3. Choose browser and whether to open in incognito mode.
4. The generated HTML page will be uploaded to S3 and opened in your browser.

Supports Chrome, Edge, & Firefox

### **Files Created**

- `page_embed_viewer.html`: temporary HTML output
- `last_embed.txt`: stores your last iframe input
- `last_browser.txt`: stores your browser preference

These are safe to delete at any time.

---

## **Reminder**

Never share your AWS credentials. This app reads them from your local `~/.aws/credentials` file.
