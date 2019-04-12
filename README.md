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

# Running
On Mac/Linux: open a terminal, then
`$ ./stdl.py -d output [Sports Tracker user ID]`
