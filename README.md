# Virtualenv & Fish
1. If you haven't set up virtualenv, then set it up by:
    ```
    $ python3 -mvenv venv
    ```
1. If you're using the Fish shell: before activating the virtualenv, check the deactivation function in  `./venv/bin/activate.fish` for the following. There exists an `if test -n "$_OLD_FISH_PROMPT_OVERRIDE"` -block. The first line of code inside that block must be `set -l fish_function_path`. Without that line, the script tries to clear the *fish_prompt*, and does not succeed in clearing the prompt, because fish apparently automatically loads *fish_prompt* from *$fish_function_path* if it exists.
1. Now you can activate the virtualenv:
    ```
    $ . venv/bin/activate.fish
    ```
1. Download ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/home
1. Make sure that your Chrome and ChromeDriver are the same version. ChromeDriver complains about it, if they don't match.

# Downloading From Sports Tracker
On Mac/Linux: open a terminal, then
`$ ./stdl.py -d output [Sports Tracker user ID]`

# Uploading To Endomondo
1. Create a file called `.env` in this directory.
1. Add the following lines to it:
    ```
    ENDOMONDO_USERNAME=your.endomondo@account.com
    ENDOMONDO_PASSWORD=y0urEnd0M0nd0Passw0rd
    ```
1. Have a directory ready containing FIT files to upload.
1. Run the script:
    ```
    $ ./endomondo-uploader.py --directory ./fit-files-directory
    ```
