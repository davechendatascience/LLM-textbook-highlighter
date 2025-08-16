# LLM-textbook-highlighter

Using perplexity ai as the LLM engine to read in a pdf and returns a highlighted version of the pdf. This pdf can be as large as a textbook with hundreds of pages.

The user may need a perplexity pro api-key to access this project.

To install under the windows environment, please run the install.ps1 under powershell, this will create a virtual environment and automatically install all the packages needed for running in the requirements.txt.

You should have a json file with the format as follows
```
{
    "perplexity_api_key": "secret"
}
```
