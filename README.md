# MetroFinalProject

The group project for the first semester of Metropolia

## INSTALL

* Virtual Environment
    It is recommended to use a `virtualenv` for installation, which is helpful for isolating dependency packages between projects.
    ```
    pip install virtualenv
    virtualenv my_env
    source my_env/bin/activate
    ```
    Then you can install the package in a virtual environment dedicated to this project.

* Dependent software packages installation
    ```
    pip install -r requirements.txt
    ```

* Add `local_config.py` and set variables such as db_user, db_pass inside it to overwrite the variables in config.py.
    ```
    db_user = 'your_db_username'
    db_pass = 'your_db_password'
    ...
    ```

* Initialize database first:
    ```
    python pilot.py initdb
    ```

* Run the game API server by:
    ```
    python pilot.py run
    ```
