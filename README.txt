                         / SR Tracker /

                 a Dell EMC SAM tool


    ~ What is SR Tracker?

      A sqlite/Flask powered SR and RCM activity tracking application

    ~ How do I use it?

      1. edit the configuration in the factory.py file or
         export an FLASKR_SETTINGS environment variable
         pointing to a configuration file or pass in a
         dictionary with config values using the create_app
         function.

      2. install the app from the root of the project directory

         pip install --editable .

      3. Instruct flask to use the right application

         export FLASK_APP=flaskr.factory:create_app()

      4. initialize the database with this command:

         flask initdb

      5. now you can run flaskr:

         flask run

         the application will greet you on
         http://localhost:7000/

    ~ Is it tested?

      You betcha.  Run `python setup.py test` to see
      the tests pass.
