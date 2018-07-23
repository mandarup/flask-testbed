





## running test_umongo.py

    $ python test_umongo.py

    $ sudo apt-get install httpie

point browser to  http://localhost:5000/users, page should display list of
default users.

Next, test adding new user:

    $ http -v POST http://localhost:5000/users firstname=carbon lastname=black nick=coal

Refresh browser and it should be updated in list of users.
Next, to see specific user, e.g. `coal`, point browser to
 http://localhost:5000/users/coal
Test modifying user attributes:

    $ http -v PATCH http://localhost:5000/users/coal lastname='diamond'

refresh browser at  http://localhost:5000/users/coal to verify changes
in modified date and modified attributes.
