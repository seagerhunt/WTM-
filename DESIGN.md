Front-end:

We utilized the idea of making one main layout.html, and extending its components to all of our other
child pages. Since each page was going to carry the same Navbar as well as a similar background and appearance,
we thought it would be efficient to carry out this method. So in our layout.html, we have the header allocated to
retrieve bootstrapping links we use as well as the link to the style css. In our body, we install the bootstrapped
navbar to display on all pages, as well as a subcomponent in Jinja designed to display flashed messages in a styled alert at the top of the page (inside the header) and provide a main content area that can be customized by extending or including this template in other templates.

We then have 11 child pages that extends this layout.html, and these are all 11 pages that users can possibly encounter. In each of these pages, there are specific design tags to customize each page, ranging from tables, headers, checkboxes, input boxes, etc., in which it may pull or implement user inputs back and forth in accordance to our app.py. We utilize the {{}} and
for loops inside html to print matching information from our WTM database with 6 tables. Two pages, preferences and searched, will not be accessible through the navbar by the user, and will simply be accessed as sub pages from profile to preferences and search to searched.

We designed it in this way since the navbar and error checking we utilized for the layout stays constant among all of the pages as we wanted the navbar availables at all times so users can traverse through the pages on their own. We found it most efficient to simply extend this layout to all of our other pages. For the general style like the purple background, I implemented formatting from styles.css, in which I linked via the head in layout.html, by using body tags in the styles.css to format the general background and font details. For page specific customization like the checkboxes or table formatting, I assigned specific classes to these tags in their own HTML pages and formatted them in my styles.css by addressing these classes with ".(class name)".

For aesthetics in my styles.css, I implemented banner style header backgrounds with different color gradients, as well as pasting a map of the northeast US in my homepage. For the tables displayed to the users, we customized the output to have more bold feeling.

Database:

We utilized sqlite3 to create tables: events, users, ratings, preferences, attendance, and descriptions. Events tables include all the information about an event including event id, name, location, commments, date, etc. This event_id serves as the primary key to different tables like rating, descriptions, and attendance which utilize this id as a foreign key to keep track of all information regarding its own table. Users table has the username, hashed password, and also carries a primary key in user_id which is also used in ratings, preferences, attendance tables.The ratings table includes both of these two elements and a rating out of 10 and a comment component to include all the text feedback. Preferences table includes the user-id as well as the adjective describing the preference. Descriptions table is for the event's adjective in which we use to match the events with. Attendance table takes in both user and event id and carries a "attended" variable from either 0 to 1. We made this separate because there are multiple attendance values per event and per people to traverse through.

Overall, we implemented SQL, more specifically sqlite3, to quickly create/insert/manage our database that we pull data from to display. We incorporated tables that could join with each other via the use of primary and foreign key ids to pull necessary data and most of our app.py consists of doing this through the db.execute function. This gave us the right values to pass to our front-end, printing this value out so users can view their recommendations, search options, etc.

Back-end:

We used two python files: app.py and helpers.py.

Helpers.py simply carries two helper function that defines the apology function as well as the login encryption that we actively incorporate in our app.py.

We use the apology function to display an error message to the user. It takes a string as an argument and returns a response object that generates an HTML error page with the given message. We found this useful since we can run this apology page out, handling errors while providing feedback to the user in a web application, so users know what they did wrong.
The login_required function serves as the login encryption helper function that utilizes a python decoreator to check if a user is logged in (via checking if "user_id" exists in the session). If the user is not logged in, it redirects them to the login page. If the user is logged in, it proceeds to execute the original function.


In our app.py, we defined our routes to and from the different pages or endpoints of our WTM application and their corresponding view functions. But first, we imported many functions and applications.
Import: To traverse through the databases with sqlite3, we imported the SQL class we used from the CS50 library to interact with our databases in the way we learned how to.Then, we imported flask and its necessary objects from the Flask library to create and manage the web application we created by flask run. From the flask_session library, we imported the Session object so we can use and personalize the web application to a specific user session id, and generally manage user sessions in the web application. Next, we imported two functions from ther werkzeug.security module to make handling user passwords more secure and also implement the hashing we learned previously. Finally, I imported the two function that we defined in helpers.py to make easier the error-posting process through the apology function and restriction process to include only logged-in users via the login_required function.

After the imports, we configured the flask application, using the location of the module passed here as a starting point when it needs to load our template files. We also configure session to be non-permanent and to utilize the filesystem to store session data. Additionally, we configure the CS50 Library to use our created SQLite database "wtm.db" in our app.py.

We have 12 functions: after_request, index, add, login, logout, preferences, profile, ratings, recommendations, register,search, and searched. For the start of each function, we use a decorator in Flask that tells Flask that the function immediately following should be called when a user makes a GET or POST request or both to the specific "/" URL of our application. These functions all contain components that help deliver a quality performance by interacting with specific user responses in the different pages. For each function we define in app.py, we attached specific comments on why we implemented each section of code. Generally, inside each function, we split them  up by its request method, and performed on our database using SQL to make adjustments based on input or create variables to print out a personalized display through our HTML pages. For example, we passed event_info in our preference function to print all the information of the event created to display that in our page using event_info as the loop head ( for x in event_info). At the end, we would either redirect the user to the corresponding page by using "redirect()" or render the HTML template by using the name of the corresponding HTML template file as an argument and rendering it into an HTML response that can be sent to the client's browser, passing some variable that could be implemented in each HTML page ("render_template, var=var"). Often in the code, we utilize session to pull the data correspondent to user id logged in session at the moment, as well as some try-catch to catch any errors in the user input, in which we resolve by posting the apology template.

List of all files:
.HTML: add, apology, index, layout, login, preferences, profile, ratings, recommendations, register, search, searched
.py: app, helpers
.md: DESIGN,README
.db: wtm
styles.css, 3 flask_session files, requirements.txt for required libraries

